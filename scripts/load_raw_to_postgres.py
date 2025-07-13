import os
import json
import logging
from datetime import datetime
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/loading.log"),
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
DATA_LAKE_PATH = "data/raw/telegram_messages"


def create_raw_table(conn):
    """Creates the raw schema and table if they don't exist."""
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw.raw_messages (
                id SERIAL PRIMARY KEY,
                message_jsonb JSONB NOT NULL,
                source_file_path TEXT NOT NULL,
                channel_name TEXT NOT NULL,
                loaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        conn.commit()
        logging.info("Schema 'raw' and table 'raw_messages' are ready.")

def load_data():
    """Walks the data lake and loads new JSON files into PostgreSQL."""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        create_raw_table(conn)

        with conn.cursor() as cur:
            for date_folder in os.listdir(DATA_LAKE_PATH):
                date_path = os.path.join(DATA_LAKE_PATH, date_folder)
                for channel_folder in os.listdir(date_path):
                    channel_path = os.path.join(date_path, channel_folder)
                    logging.info(f"Processing directory: {channel_path}")
                    for filename in os.listdir(channel_path):
                        if filename.endswith(".json"):
                            file_path = os.path.join(channel_path, filename)

                            cur.execute("SELECT 1 FROM raw.raw_messages WHERE source_file_path = %s", (file_path,))
                            if cur.fetchone():
                                continue

                            with open(file_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                cur.execute(
                                    "INSERT INTO raw.raw_messages (message_jsonb, source_file_path, channel_name) VALUES (%s, %s, %s)",
                                    (Json(data), file_path, channel_folder)
                                )
            conn.commit()
            logging.info("Successfully loaded new raw data into PostgreSQL.")

    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    load_data()