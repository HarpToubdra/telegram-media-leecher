import os
import re
from typing import Tuple, Dict, Any
from guessit import guessit
from .config import Config

VALID_EXTS = (".mp4", ".mkv", ".avi", ".mov", ".ts", ".m4v", ".webm", ".flv")
ADULT_KEYWORDS = ["adulte", "xxx", "porn", "hentai", "nsfw"]
ANIME_KEYWORDS = ["anime", "manga", "vostfr"]

def sanitize_name(name: str) -> str:
    """Removes or replaces invalid filesystem characters."""
    # Replace characters not allowed in filenames
    cleaned = re.sub(r'[\\/*?:"<>|]', '', name)
    # Remove leading/trailing spaces and dots
    cleaned = cleaned.strip('. ')
    return cleaned if cleaned else "Unknown"

def get_valid_extension(file_name: str) -> str:
    """Returns the valid video extension if present at the end of the filename, else .mkv."""
    lower = file_name.lower()
    for ext in VALID_EXTS:
        if lower.endswith(ext):
            return ext
    return ".mkv"

def route_media(file_name: str, caption_text: str, config: Config) -> Tuple[str, Dict[str, Any]]:
    """
    Analyzes filename and caption using GuessIt and keyword heuristics
    to determine the destination directory.
    Returns (dest_dir, metadata).
    """
    caption_lower = (caption_text or "").lower()
    fname_lower = (file_name or "").lower()

    is_adult = any(tag in caption_lower or tag in fname_lower for tag in ADULT_KEYWORDS)
    is_anime_explicit = any(tag in caption_lower or tag in fname_lower for tag in ANIME_KEYWORDS)

    # Parse metadata from filename
    guess = guessit(file_name)
    title = guess.get("title", "Vrac")
    year = guess.get("year")
    season = guess.get("season")
    episode = guess.get("episode")
    media_type = guess.get("type", "unknown")

    safe_title = sanitize_name(str(title))
    if year and media_type == "movie":
        safe_title = f"{safe_title} ({year})"

    # Decision tree: Adult vs Anime vs TV Series vs Movie
    if is_adult:
        category = "adult"
        dest_dir = config.download_dir_adulte
    elif is_anime_explicit:
        category = "anime"
        if season is not None:
            try:
                season_num = int(season)
            except (ValueError, TypeError):
                season_num = 1
            dest_dir = os.path.join(config.download_dir_animes, safe_title, f"Season {season_num:02d}")
        elif episode is not None:
            dest_dir = os.path.join(config.download_dir_animes, safe_title, "Season 01")
        else:
            dest_dir = os.path.join(config.download_dir_animes, safe_title)
    elif media_type == "episode" or season is not None or episode is not None:
        category = "series"
        season_num = 1
        if season is not None:
            try:
                season_num = int(season)
            except (ValueError, TypeError):
                season_num = 1
        dest_dir = os.path.join(config.download_dir_series, safe_title, f"Season {season_num:02d}")
    else:
        category = "movie"
        dest_dir = os.path.join(config.download_dir_films, safe_title)

    os.makedirs(dest_dir, exist_ok=True)
    return dest_dir, {
        "title": safe_title,
        "season": season,
        "episode": episode,
        "category": category,
        "media_type": category,
        "extension": get_valid_extension(file_name),
        "guess": guess
    }
