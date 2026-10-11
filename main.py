#!/usr/bin/env python3
"""
Telegram Media Leecher
Automated downloader for media forwarded in Telegram groups directly to Jellyfin/Plex/Emby.
"""

import sys
import logging
import asyncio
from src.config import load_config
from src.bot import setup_bot

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

async def main():
    configure_logging()
    logger = logging.getLogger("telegram_leecher.main")
    logger.info("Starting Telegram Media Leecher...")

    config = load_config()
    logger.info("Configuration loaded successfully.")
    logger.info("Target Telegram chat: %s", config.target_chat)
    logger.info("Films directory: %s", config.download_dir_films)
    logger.info("Series directory: %s", config.download_dir_series)
    logger.info("Animes directory: %s", config.download_dir_animes)

    client = setup_bot(config)

    # Start Telethon client (prompts for phone number/code on first run if session doesn't exist)
    logger.info("Connecting to Telegram...")
    await client.start()

    me = await client.get_me()
    logger.info("Connected as @%s (%s)", getattr(me, 'username', 'N/A'), me.first_name)
    logger.info("Listening for new forwarded videos in '%s'...", config.target_chat)

    try:
        await client.run_until_disconnected()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping Telegram Media Leecher gracefully...")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete.")
