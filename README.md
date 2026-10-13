# Telegram Media Leecher

**Automated media downloader from Telegram channels & chats directly to your Jellyfin, Plex, or Emby media library.**

[Lire en français](README.fr.md) · [Configuration example](.env.example) · [Contributing](CONTRIBUTING.md) · [License](LICENSE)

## What it does

Telegram Media Leecher monitors a dedicated Telegram chat or group for forwarded or uploaded video files and automatically downloads them directly to your media storage server:

- **Direct Telegram downloader**: Downloads media directly from Telegram's content delivery servers using hardware-accelerated AES decryption (`cryptg`). No BitTorrent, no peer-to-peer uploads, no ratio requirements, and no ISP / Arcom tracking.
- **Automated classification**: Uses [GuessIt](https://guessit-io.github.io/guessit/) and keyword rules to parse release names and route files to movies, TV series, anime, or adult media folders.
- **Clean library formatting**: Automatically structures shows into `Title/Season XX/` directories and preserves exact file extensions (even for releases containing dots in their titles).
- **Safe permissions**: Sets file permissions to `0666` upon completion so media servers running under different service accounts can immediately read and stream the files.
- **Anti-flood progress reporting**: Displays a dynamic, throttled progress bar with downloaded megabytes/gigabytes in Telegram without triggering Telegram `FloodWait` cooldowns.
- **Media server webhook**: Sends an automated refresh signal to your Jellyfin, Emby, or Plex instance as soon as a download finishes.

## How it works

~~~text
Telegram Channel / Chat (Any public or private source)
                     │
                     │ (Forward / Post video)
                     ▼
       Dedicated Telegram Group (e.g. Jellyfin)
                     │
                     ▼
  Telegram Media Leecher (Telethon + GuessIt)
                     │
                     ├── Parse filename & metadata
                     │   ├── Movies       ──> /media/films/Title (Year)/
                     │   ├── TV Series    ──> /media/series/Title/Season XX/
                     │   ├── Anime        ──> /media/animes/Title/Season XX/
                     │   └── Adult media  ──> /media/adulte/
                     │
                     └── Trigger library scan ──> Jellyfin / Emby (HTTP API)
~~~

## Requirements

| Component | Requirement |
| --- | --- |
| Telegram API | `TG_API_ID` and `TG_API_HASH` obtained from [my.telegram.org](https://my.telegram.org) |
| Application host | Linux, Python 3.10 or newer (or Docker / Docker Compose) |
| Storage paths | Local or mounted NFS/SMB directories for media libraries |
| Media server (optional) | Jellyfin, Plex, or Emby with an API key to enable instant library scans |

## Quickstart with Docker Compose

### Option A: One-command guided installation (Recommended)

From this project directory, run:

~~~bash
./install.sh
~~~

The script validates requirements, prompts for API credentials and paths, sets `umask 077` permissions, helps authenticate the one-time Telegram session, and starts the container.

### Option B: Manual configuration

1. Copy the example configuration:
   ~~~bash
   cp .env.example .env
   nano .env
   ~~~
2. Run one-time Telegram authentication:
   ~~~bash
   docker compose run --rm telegram-leecher python main.py
   ~~~
3. Start the service:
   ~~~bash
   docker compose up -d
   docker compose logs -f
   ~~~

## Bare-metal and LXC installation (systemd)

For Debian, Ubuntu, or Proxmox LXC containers:

### 1. Install system dependencies

~~~bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git gcc libffi-dev build-essential
~~~

### 2. Clone the repository to `/opt`

~~~bash
sudo git clone https://github.com/HarpToubdra/telegram-media-leecher.git /opt/telegram-media-leecher
cd /opt/telegram-media-leecher
~~~

### 3. Create virtual environment and install dependencies

~~~bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
~~~

### 4. Set up configuration and authenticate

~~~bash
cp .env.example .env
nano .env
.venv/bin/python main.py
~~~

Authenticate with your phone number and SMS code, then stop the process with `Ctrl+C`.

### 5. Enable and start systemd service

~~~bash
sudo cp systemd/telegram-leecher.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now telegram-leecher
sudo journalctl -u telegram-leecher -f
~~~

## Configuration reference

| Setting | Default | Purpose |
| --- | --- | --- |
| `TG_API_ID` | empty | Telegram API numeric ID from my.telegram.org |
| `TG_API_HASH` | empty | Telegram API hash string from my.telegram.org |
| `TG_SESSION_PATH` | `./data/telegram_session` | Path where Telethon saves the persistent session file |
| `TARGET_CHAT` | `Jellyfin` | Exact chat title or numeric ID of the monitored group |
| `DOWNLOAD_DIR_FILMS` | `/media/films` | Destination folder for movies |
| `DOWNLOAD_DIR_SERIES` | `/media/series` | Destination folder for regular TV series |
| `DOWNLOAD_DIR_ANIMES` | `/media/animes` | Destination folder for anime and Japanese animation |
| `DOWNLOAD_DIR_ADULTE` | `/media/adulte` | Destination folder for adult content |
| `JELLYFIN_ENABLED` | `false` | Enable automatic library refresh when download completes |
| `JELLYFIN_URL` | `http://localhost:8096` | Base URL of the Jellyfin server |
| `JELLYFIN_API_KEY` | empty | API token created in Jellyfin Dashboard > API Keys |

Real environment variables take precedence over values in `.env`. The parser accepts standard `KEY=VALUE` pairs.

## Organization rules

| Category | Destination pattern | Routing conditions |
| --- | --- | --- |
| **Movies** | `/media/films/<Title> (<Year>)/` | Default category when no episodic numbering or special tags are found |
| **TV Series** | `/media/series/<Title>/Season <XX>/` | Filename or text contains episodic numbering (e.g. `S01E04`, `1x04`) |
| **Anime** | `/media/animes/<Title>/Season <XX>/` | Caption or filename contains `anime`, `manga`, or `vostfr` tags |
| **Adult media** | `/media/adulte/` | Caption or filename contains keywords (`adulte`, `xxx`, `porn`, `hentai`, `nsfw`) |

## Troubleshooting

| Symptom | Check |
| --- | --- |
| “Missing TG_API_ID or TG_API_HASH” | Define both credentials in `.env` or in the systemd service environment. |
| Telegram prompts for phone number on startup | Expected on initial run. Start the process once in an interactive terminal to generate `./data/telegram_session.session`. |
| `FloodWaitError` when downloading or editing messages | Telegram rate limits rapid message edits. Progress messages are automatically throttled to 3.5-second intervals. |
| Jellyfin returns HTTP 401 Unauthorized | Check `JELLYFIN_API_KEY`. The bot automatically provides both `Authorization: MediaBrowser Token="..."` and `X-Emby-Token` headers. |
| Jellyfin cannot read downloaded files | The bot runs `chmod 0666` on completed files. Ensure Jellyfin's user has execute (`+x`) permissions on parent directories. |
| Video routed to movies instead of anime | Add the keyword `anime` or `vostfr` in the message caption when forwarding the file. |

## Security and limits

- **Protect the session file**: The `.session` file stores full access tokens for your Telegram account. Never commit `.session` or `.env` files to public git repositories. Keep `./data` outside version control.
- **Telegram rate limits**: Telegram imposes bandwidth and file size limits according to account tier (up to 2 GB for standard accounts, up to 4 GB for Telegram Premium accounts).
- **Sequential downloads**: Downloads are handled sequentially per bot instance to avoid connection flood bans and protect disk I/O.
- **File permissions**: Downloaded media is marked `0666` (`rw-rw-rw-`) to ensure interoperability across shared storage, Samba mounts, and containerized media servers.

## Development and tests

~~~bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
pytest -v
~~~

## License

MIT. See [LICENSE](LICENSE).
