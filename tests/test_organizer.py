import os
import pytest
from src.config import Config
from src.organizer import sanitize_name, get_valid_extension, route_media

@pytest.fixture
def mock_config(tmp_path):
    films_dir = str(tmp_path / "films")
    series_dir = str(tmp_path / "series")
    animes_dir = str(tmp_path / "animes")
    adulte_dir = str(tmp_path / "adulte")
    return Config(
        api_id=12345,
        api_hash="dummyhash",
        session_path=str(tmp_path / "session"),
        target_chat="Jellyfin",
        download_dir_films=films_dir,
        download_dir_series=series_dir,
        download_dir_animes=animes_dir,
        download_dir_adulte=adulte_dir,
        jellyfin_enabled=False,
        jellyfin_url="http://localhost:8096",
        jellyfin_api_key="dummy_key",
    )

def test_sanitize_name():
    assert sanitize_name('Movie: The "Reckoning"?') == "Movie The Reckoning"
    assert sanitize_name("  ...Test Title...  ") == "Test Title"
    assert sanitize_name("") == "Unknown"

def test_get_valid_extension():
    assert get_valid_extension("video.mkv") == ".mkv"
    assert get_valid_extension("video.MP4") == ".mp4"
    assert get_valid_extension("show.s01e01.avi") == ".avi"
    assert get_valid_extension("movie.without.valid.ext") == ".mkv"

def test_route_movie(mock_config):
    dest, meta = route_media("Inception.2010.1080p.BluRay.mkv", "", mock_config)
    assert meta["category"] == "movie"
    assert "Inception (2010)" in dest
    assert dest.startswith(mock_config.download_dir_films)

def test_route_series(mock_config):
    dest, meta = route_media("Breaking.Bad.S02E05.720p.mkv", "", mock_config)
    assert meta["category"] == "series"
    assert meta["season"] == 2
    assert "Season 02" in dest
    assert dest.startswith(mock_config.download_dir_series)

def test_route_anime_with_caption(mock_config):
    dest, meta = route_media("Jujutsu.Kaisen.S01E03.1080p.mp4", "Super épisode en vostfr manga", mock_config)
    assert meta["category"] == "anime"
    assert "Season 01" in dest
    assert dest.startswith(mock_config.download_dir_animes)

def test_route_adult_content(mock_config):
    dest, meta = route_media("Private.Collection.XXX.mp4", "", mock_config)
    assert meta["category"] == "adult"
    assert dest == mock_config.download_dir_adulte

def test_route_adult_with_caption(mock_config):
    dest, meta = route_media("Documentary.mp4", "Vidéo réservée aux adultes (adulte)", mock_config)
    assert meta["category"] == "adult"
    assert dest == mock_config.download_dir_adulte

def test_route_dotted_title(mock_config):
    dest, meta = route_media("A.I.C.O. -Incarnation- E01.mkv", "anime", mock_config)
    assert meta["category"] == "anime"
    assert dest.startswith(mock_config.download_dir_animes)
