import os
import re
from typing import Tuple, Dict, Any
from guessit import guessit
from .config import Config

def sanitize_name(name: str) -> str:
    """Removes or replaces invalid filesystem characters."""
    # Replace characters not allowed in filenames
    cleaned = re.sub(r'[\\/*?:"<>|]', '', name)
    # Remove leading/trailing spaces and dots
    cleaned = cleaned.strip('. ')
    return cleaned if cleaned else "Unknown"

def route_media(file_name: str, caption_text: str, config: Config) -> Tuple[str, Dict[str, Any]]:
    """
    Analyzes filename and caption using GuessIt to determine the destination directory.
    Returns (dest_dir, metadata).
    """
    caption_lower = (caption_text or "").lower()
    is_anime_explicit = any(tag in caption_lower for tag in ["anime", "manga", "vostfr"])

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

    # Decision tree: Anime vs TV Series vs Movie
    if is_anime_explicit:
        # User tagged as anime or caption indicates anime
        if season is not None:
            season_num = int(season) if str(season).isdigit() else 1
            dest_dir = os.path.join(config.download_dir_animes, safe_title, f"Season {season_num:02d}")
        elif episode is not None:
            dest_dir = os.path.join(config.download_dir_animes, safe_title, "Season 01")
        else:
            dest_dir = os.path.join(config.download_dir_animes, safe_title)
    elif media_type == "episode" or season is not None or episode is not None:
        # Regular TV series
        season_num = 1
        if season is not None:
            try:
                season_num = int(season)
            except (ValueError, TypeError):
                season_num = 1
        dest_dir = os.path.join(config.download_dir_series, safe_title, f"Season {season_num:02d}")
    else:
        # Default to Movie
        dest_dir = os.path.join(config.download_dir_films, safe_title)

    os.makedirs(dest_dir, exist_ok=True)
    return dest_dir, {
        "title": safe_title,
        "season": season,
        "episode": episode,
        "media_type": "anime" if is_anime_explicit else media_type,
        "guess": guess
    }
