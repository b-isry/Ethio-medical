# enrich_images.py

import os
import logging
import psycopg2
from dotenv import load_dotenv
from ultralytics import YOLO

# --- Basic Configuration ---
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/enrichment.log"),
        logging.StreamHandler()
    ]
)
os.makedirs("logs", exist_ok=True)

# --- Database Connection Details ---
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# --- Source Data Directory ---
IMAGE_LAKE_PATH = "data/raw/images"

def create_raw_detections_table(conn):
    """Creates the raw schema and table for image detections if they don't exist."""
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw.raw_image_detections (
                id SERIAL PRIMARY KEY,
                message_id BIGINT NOT NULL,
                detected_object VARCHAR(255) NOT NULL,
                confidence_score REAL NOT NULL,
                source_image_path TEXT,
                loaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        conn.commit()
        logging.info("Schema 'raw' and table 'raw_image_detections' are ready.")

def process_images():
    """Scans for images, runs YOLO detection, and loads results into PostgreSQL."""
    logging.info("Starting image enrichment process...")

    model = YOLO('yolov8n.pt')
    logging.info("YOLOv8 model loaded successfully.")

    conn = None
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        create_raw_detections_table(conn)

        with conn.cursor() as cur:
            for date_folder in os.listdir(IMAGE_LAKE_PATH):
                date_path = os.path.join(IMAGE_LAKE_PATH, date_folder)
                if not os.path.isdir(date_path): continue

                for channel_folder in os.listdir(date_path):
                    channel_path = os.path.join(date_path, channel_folder)
                    if not os.path.isdir(channel_path): continue

                    logging.info(f"Scanning for images in: {channel_path}")
                    for filename in os.listdir(channel_path):
                        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                            image_path = os.path.join(channel_path, filename)
                            message_id = os.path.splitext(filename)[0]

                            # Run YOLOv8 inference on the image
                            results = model(image_path)

                            # Make the process idempotent: clear old detections for this message
                            cur.execute("DELETE FROM raw.raw_image_detections WHERE message_id = %s", (message_id,))

                            # Process and insert new results
                            detection_count = 0
                            for r in results:
                                for box in r.boxes:
                                    class_id = int(box.cls[0])
                                    confidence = float(box.conf[0])
                                    detected_class = model.names[class_id]
                                    
                                    # Only save detections with a reasonable confidence score
                                    if confidence > 0.4:
                                        cur.execute(
                                            """
                                            INSERT INTO raw.raw_image_detections
                                            (message_id, detected_object, confidence_score, source_image_path)
                                            VALUES (%s, %s, %s, %s)
                                            """,
                                            (message_id, detected_class, confidence, image_path)
                                        )
                                        detection_count += 1
                            
                            if detection_count > 0:
                                logging.info(f"Inserted {detection_count} detections for message_id {message_id}.")

            conn.commit()
            logging.info("Successfully finished image enrichment process.")

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    process_images()
    