<div align="center">

# 🚀 Telegram Media Leecher

**Automated media downloader from Telegram channels & chats directly to your Jellyfin, Plex, or Emby media library.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Telethon](https://img.shields.io/badge/Powered%20By-Telethon-blue)](https://github.com/LonamiWebs/Telethon)

</div>

---

## 🌟 Why Telegram Media Leecher?

Unlike traditional *arr bots (like *Addarr* or *Sonarr-Telegram-Bot*) that only query BitTorrent trackers:
* 📥 **Direct Telegram Downloader**: Downloads high-definition video files directly hosted on Telegram servers at maximum connection speeds.
* 🛡️ **Private & Safe**: No BitTorrent, no P2P sharing, no upload ratio requirements, and no ISP / Arcom warnings.
* 🤖 **Smart Organization with GuessIt**: Automatically parses messy release titles and organizes your files into `Movies/Title (Year)` or `Series/Title/Season XX/`.
* 📊 **Live Progress Bar**: Displays a throttled, anti-flood visual progress bar with downloaded megabytes/gigabytes.
* 🍿 **Jellyfin Auto-Refresh**: Immediately notifies your Jellyfin media server to scan new libraries once a file is finished.

---

## 🏗️ How It Works

```mermaid
graph LR
    A[Canaux Telegram privés] -->|Transfert / Forward| B[Groupe Telegram Dédié : Jellyfin]
    B --> C[Telegram Media Leecher]
    C -->|Parse GuessIt & Tri| D[Stockage Serveur / NAS]
    D -->|Films| D1[/media/films]
    D -->|Séries| D2[/media/series]
    D -->|Animes| D3[/media/animes]
    C -->|API Refresh| E[Jellyfin / Plex / Emby]
```

1. You forward any video file from any Telegram channel into your private group (e.g., `Jellyfin`).
2. The bot starts downloading the file to your server with hardware-accelerated AES decryption (`cryptg`).
3. The video is automatically classified, moved to the right folder, and available on your TV!

---

## 📋 Prerequisites

Before starting, get your free Telegram API credentials:
1. Log in to [my.telegram.org](https://my.telegram.org).
2. Go to **API development tools**.
3. Create a new application (title and short name can be anything).
4. Save your **`api_id`** (numeric) and **`api_hash`** (alphanumeric string).

---

## 🐳 Quickstart with Docker (Recommended)

### 1. Clone the repository
```bash
git clone https://github.com/your-username/telegram-media-leecher.git
cd telegram-media-leecher
```

### 2. Configure `.env`
Copy the template and fill in your credentials:
```bash
cp .env.example .env
nano .env
```

### 3. Adjust `docker-compose.yml` volumes
Update host paths in `docker-compose.yml` to point to your media directories:
```yaml
volumes:
  - ./data:/app/data
  - /mnt/storage/films:/media/films
  - /mnt/storage/series:/media/series
  - /mnt/storage/animes:/media/animes
```

### 4. First run & Telegram Authentication
On the first run, Telegram requires your phone number and verification code:
```bash
docker compose run --rm telegram-leecher
```
*Enter your phone number (international format e.g., `+336...`) and the verification code sent to your Telegram app.*
Once authenticated, the session is safely saved inside `./data/`.

### 5. Start in Background
```bash
docker compose up -d
docker compose logs -f
```

---

## 🐧 Bare-Metal & LXC Installation (Systemd)

If you run Proxmox LXC, Debian, or Ubuntu:

```bash
# 1. Install system requirements
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git gcc libffi-dev

# 2. Clone to /opt
sudo git clone https://github.com/your-username/telegram-media-leecher.git /opt/telegram-media-leecher
cd /opt/telegram-media-leecher

# 3. Create virtual environment & install requirements
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. Configure .env
cp .env.example .env
nano .env

# 5. First-time login (interactive)
python3 main.py
# (Enter phone number & Telegram SMS code, then press Ctrl+C once verified)

# 6. Enable systemd service
sudo cp systemd/telegram-leecher.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now telegram-leecher
sudo journalctl -u telegram-leecher -f
```

---

## ⚙️ Configuration Reference (`.env`)

| Variable | Description | Default |
|---|---|---|
| `TG_API_ID` | Your Telegram API ID from my.telegram.org | *Required* |
| `TG_API_HASH` | Your Telegram API Hash from my.telegram.org | *Required* |
| `TG_SESSION_PATH` | Path where the session file will be stored | `./data/telegram_session` |
| `TARGET_CHAT` | Title or ID of the Telegram group to monitor | `Jellyfin` |
| `DOWNLOAD_DIR_FILMS` | Destination directory for movies | `/media/films` |
| `DOWNLOAD_DIR_SERIES` | Destination directory for regular TV series | `/media/series` |
| `DOWNLOAD_DIR_ANIMES` | Destination directory for animes / mangas | `/media/animes` |
| `JELLYFIN_ENABLED` | Set to `true` to enable auto-scan | `false` |
| `JELLYFIN_URL` | Base URL of your Jellyfin server | `http://localhost:8096` |
| `JELLYFIN_API_KEY` | Jellyfin API token (from Dashboard > API Keys) | `""` |

---

## 💡 Tips & Organization Rules

* **Anime Sorting**: Add the word **`anime`**, **`manga`**, or **`vostfr`** in the caption when forwarding a file. The bot will automatically route it to `DOWNLOAD_DIR_ANIMES/Title/Season XX/`.
* **Episodes & Seasons**: If the filename contains season/episode numbering (e.g., `S01E04`, `1x04`), the bot will create proper subdirectories formatted as `Season 01/`.
* **Anti-Flood Protection**: Telegram restricts message editing frequency. Progress updates are automatically throttled every 3.5 seconds to avoid `FloodWait` cooldowns.

---

## 🔒 Security & Privacy

* **Never commit your `.env` or `*.session` files.** The `.gitignore` provided with this repository already ignores them by default.
* Your session string gives full access to your Telegram account. Keep it private.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
