import logging
import requests
from .config import Config

logger = logging.getLogger("telegram_leecher.notifier")

def trigger_jellyfin_refresh(config: Config) -> bool:
    """Triggers a library refresh on the configured Jellyfin instance."""
    if not config.jellyfin_enabled:
        return False

    if not config.jellyfin_api_key:
        logger.warning("Jellyfin is enabled but JELLYFIN_API_KEY is empty.")
        return False

    url = f"{config.jellyfin_url}/Library/Refresh"
    headers = {
        "X-Emby-Token": config.jellyfin_api_key,
        "Accept": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, timeout=10)
        if response.status_code in (200, 204):
            logger.info("Successfully triggered Jellyfin library refresh.")
            return True
        else:
            logger.warning("Jellyfin refresh returned status %s: %s", response.status_code, response.text)
            return False
    except Exception as exc:
        logger.error("Failed to connect to Jellyfin at %s: %s", url, exc)
        return False
