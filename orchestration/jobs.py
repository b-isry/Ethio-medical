import subprocess
from dagster import job, op, get_dagster_logger

DBT_PROJECT_DIR = "/app/ethio_medical_dbt"

@op
def scrape_telegram_data_op():
    """
    An op to run the Telegram scraping script.
    """
    logger = get_dagster_logger()
    logger.info("Starting Telegram scraping process...")
    
    # Use subprocess to run the script. check=True ensures that if the script
    # fails (returns a non-zero exit code), the op will fail.
    subprocess.run(["python", "/app/scripts/scraper.py"], check=True)
    
    logger.info("Telegram scraping finished successfully.")
    return True # Return a value to signal success to downstream ops

@op
def load_raw_to_postgres_op(start_signal: bool):
    """
    An op to load the raw scraped JSON files into PostgreSQL.
    This op depends on scrape_telegram_data_op finishing successfully.
    """
    logger = get_dagster_logger()
    logger.info("Starting data load from raw files to PostgreSQL...")
    
    subprocess.run(["python", "/app/scripts/load_raw_to_postgres.py"], check=True)
    
    logger.info("Data loading finished successfully.")
    return True

@op
def run_dbt_transformations_op(start_signal: bool):
    """
    An op to run `dbt build`. This transforms the raw data into our
    final star schema models. It depends on the raw data being loaded.
    """
    logger = get_dagster_logger()
    logger.info("Starting dbt transformations...")

    subprocess.run(["dbt", "build"], check=True, cwd=DBT_PROJECT_DIR)

    logger.info("dbt transformations finished successfully.")
    return True

@op
def run_yolo_enrichment_op(start_signal: bool):
    """
    An op to run the YOLOv8 image enrichment script.
    This can run in parallel with the dbt transformations, as it only
    depends on the raw data being loaded.
    """
    logger = get_dagster_logger()
    logger.info("Starting image enrichment with YOLO...")
    
    subprocess.run(["python", "/app/scripts/enrich_images.py"], check=True)
    
    logger.info("Image enrichment finished successfully.")
    return True


@job
def full_elt_pipeline():
    """
    The full Extract, Load, Transform, and Enrich job.
    This defines the dependency graph for our ops.
    """
    # 1. Scrape data from Telegram
    scrape_result = scrape_telegram_data_op()
    
    # 2. Load the raw data into PostgreSQL (depends on scraping)
    load_result = load_raw_to_postgres_op(scrape_result)
    
    # 3. After loading, we can run dbt and yolo in parallel.
    #    Dagster will handle running these at the same time if resources permit.
    run_dbt_transformations_op(load_result)
    run_yolo_enrichment_op(load_result)