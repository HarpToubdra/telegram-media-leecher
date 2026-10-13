import os
import sys
from dataclasses import dataclass
from dotenv import load_dotenv

# Load variables from .env file if present
load_dotenv()

@dataclass
class Config:
    api_id: int
    api_hash: str
    session_path: str
    target_chat: str
    download_dir_films: str
    download_dir_series: str
    download_dir_animes: str
    download_dir_adulte: str
    jellyfin_enabled: bool
    jellyfin_url: str
    jellyfin_api_key: str

def load_config() -> Config:
    raw_api_id = os.getenv("TG_API_ID")
    api_hash = os.getenv("TG_API_HASH")

    if not raw_api_id or not api_hash:
        print("[CRITICAL] Missing TG_API_ID or TG_API_HASH in environment or .env file.")
        print("Please copy .env.example to .env and fill in your credentials from https://my.telegram.org")
        sys.exit(1)

    try:
        api_id = int(raw_api_id)
    except ValueError:
        print(f"[CRITICAL] TG_API_ID must be an integer, got: {raw_api_id}")
        sys.exit(1)

    session_path = os.getenv("TG_SESSION_PATH", "./data/telegram_session")
    target_chat = os.getenv("TARGET_CHAT", "Jellyfin")

    download_dir_films = os.getenv("DOWNLOAD_DIR_FILMS", "/media/films")
    download_dir_series = os.getenv("DOWNLOAD_DIR_SERIES", "/media/series")
    download_dir_animes = os.getenv("DOWNLOAD_DIR_ANIMES", "/media/animes")
    download_dir_adulte = os.getenv("DOWNLOAD_DIR_ADULTE", "/media/adulte")

    jellyfin_enabled = os.getenv("JELLYFIN_ENABLED", "false").strip().lower() in ("true", "1", "yes")
    jellyfin_url = os.getenv("JELLYFIN_URL", "http://localhost:8096").rstrip("/")
    jellyfin_api_key = os.getenv("JELLYFIN_API_KEY", "")

    # Ensure required parent directories exist
    os.makedirs(download_dir_films, exist_ok=True)
    os.makedirs(download_dir_series, exist_ok=True)
    os.makedirs(download_dir_animes, exist_ok=True)
    os.makedirs(download_dir_adulte, exist_ok=True)
    
    # Ensure directory for session exists
    session_dir = os.path.dirname(session_path)
    if session_dir:
        os.makedirs(session_dir, exist_ok=True)

    return Config(
        api_id=api_id,
        api_hash=api_hash,
        session_path=session_path,
        target_chat=target_chat,
        download_dir_films=download_dir_films,
        download_dir_series=download_dir_series,
        download_dir_animes=download_dir_animes,
        download_dir_adulte=download_dir_adulte,
        jellyfin_enabled=jellyfin_enabled,
        jellyfin_url=jellyfin_url,
        jellyfin_api_key=jellyfin_api_key,
    )
