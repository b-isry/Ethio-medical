# scrape_telegram.py

import os
import json
import logging
from datetime import datetime
import asyncio
from dotenv import load_dotenv

from telethon.sync import TelegramClient
from telethon.tl.types import Channel

# --- Basic Configuration ---
load_dotenv()

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/scraping.log"),
        logging.StreamHandler()
    ]
)

# --- Telegram API Credentials ---
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

CHANNELS = [
    'lobelia4cosmetics',
    'tikvahpharma',
    'CheMed123',          
    'yetenaweg'      
]


async def scrape_channel(client, channel_handle):
    """
    Scrapes messages and associated media from a single Telegram channel
    and stores them in a structured data lake.
    """
    today_str = datetime.now().strftime('%Y-%m-%d')
    logging.info(f"Starting scrape for channel: {channel_handle}")

    try:
        entity = await client.get_entity(channel_handle)
    except Exception as e:
        logging.error(f"Could not find channel '{channel_handle}'. Skipping. Error: {e}")
        return

    output_dir_messages = f"data/raw/telegram_messages/{today_str}/{channel_handle}"
    output_dir_images = f"data/raw/images/{today_str}/{channel_handle}"

    os.makedirs(output_dir_messages, exist_ok=True)
    os.makedirs(output_dir_images, exist_ok=True)

    messages_saved = 0
    images_saved = 0

    async for message in client.iter_messages(entity, limit=100):
        message_data = message.to_dict()

        message_file_path = os.path.join(output_dir_messages, f"{message.id}.json")

        with open(message_file_path, 'w', encoding='utf-8') as f:
            json.dump(message_data, f, ensure_ascii=False, indent=4, default=str)
        messages_saved += 1

        if message.photo:
            photo_path = await message.download_media(file=output_dir_images)
            if photo_path:
                images_saved += 1
                logging.info(f"Saved image from message {message.id} to {photo_path}")

    logging.info(
        f"Finished scraping {channel_handle}. "
        f"Saved {messages_saved} messages and {images_saved} images."
    )


async def main():
    """
    Main function to initialize the Telegram client and run the scraping process.
    """
    async with TelegramClient('anon', API_ID, API_HASH) as client:
        for channel in CHANNELS:
            await scrape_channel(client, channel)

if __name__ == "__main__":
    asyncio.run(main())