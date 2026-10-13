# Contributing to Telegram Media Leecher

Thanks for your interest. Telegram Media Leecher is lightweight on purpose: an automated media downloader for self-hosted homelabs.

## Ground rules

- **Zero credential policy**: Never commit `.env`, `*.session`, real phone numbers, API keys, or private chat IDs into the repository, issues, or pull requests.
- **Privacy-first**: Telegram Media Leecher operates exclusively via direct Telegram server downloads without BitTorrent or peer-to-peer uploads.
- **Test coverage**: Any modification to routing, sanitization, extension handling, or notifications must be covered by unit tests in `tests/`.

## Local development & testing

Set up a virtual environment and run the test suite:

~~~bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e '.[test]'
pytest -v
~~~

## Coding standards

- Type annotations for functions and signatures (`typing`).
- Keep external runtime dependencies focused (`telethon`, `cryptg`, `guessit`, `python-dotenv`, `requests`).
- Ensure all file operations respect system permissions (`chmod 0666` for downloaded media files so Jellyfin/Plex services can read them).

## Reporting issues

Before opening an issue, verify that your Telegram session credentials (`TG_API_ID`, `TG_API_HASH`) are valid and that logs contain no sensitive tokens or private IDs.
