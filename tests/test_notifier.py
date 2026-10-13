import pytest
from unittest.mock import patch, MagicMock
from src.config import Config
from src.notifier import trigger_jellyfin_refresh

@pytest.fixture
def base_config():
    return Config(
        api_id=12345,
        api_hash="dummyhash",
        session_path="/tmp/session",
        target_chat="Jellyfin",
        download_dir_films="/tmp/films",
        download_dir_series="/tmp/series",
        download_dir_animes="/tmp/animes",
        download_dir_adulte="/tmp/adulte",
        jellyfin_enabled=True,
        jellyfin_url="http://192.168.2.26:8096",
        jellyfin_api_key="valid_token_123",
    )

def test_jellyfin_disabled(base_config):
    base_config.jellyfin_enabled = False
    assert trigger_jellyfin_refresh(base_config) is False

def test_jellyfin_empty_api_key(base_config):
    base_config.jellyfin_api_key = ""
    assert trigger_jellyfin_refresh(base_config) is False

@patch("src.notifier.requests.post")
def test_jellyfin_refresh_success(mock_post, base_config):
    mock_resp = MagicMock()
    mock_resp.status_code = 204
    mock_post.return_value = mock_resp

    result = trigger_jellyfin_refresh(base_config)
    assert result is True

    mock_post.assert_called_once()
    call_args, call_kwargs = mock_post.call_args
    assert call_args[0] == "http://192.168.2.26:8096/Library/Refresh"
    headers = call_kwargs["headers"]
    assert headers["Authorization"] == 'MediaBrowser Token="valid_token_123"'
    assert headers["X-Emby-Token"] == "valid_token_123"

@patch("src.notifier.requests.post")
def test_jellyfin_refresh_unauthorized(mock_post, base_config):
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthorized"
    mock_post.return_value = mock_resp

    result = trigger_jellyfin_refresh(base_config)
    assert result is False
