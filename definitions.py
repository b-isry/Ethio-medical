from dagster import Definitions, ScheduleDefinition
from orchestration.jobs import full_elt_pipeline

daily_refresh_schedule = ScheduleDefinition(
    job=full_elt_pipeline,
    cron_schedule="0 1 * * *",  
    execution_timezone="UTC",
)

defs = Definitions(
    jobs=[full_elt_pipeline],
    schedules=[daily_refresh_schedule],
)