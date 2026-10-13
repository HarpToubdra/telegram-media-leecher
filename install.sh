#!/usr/bin/env bash
# Guided, repeatable Docker Compose installation for Telegram Media Leecher.
set -euo pipefail

project_dir=$(cd -- "$(dirname -- "$0")" && pwd)
cd "$project_dir"

die() { printf 'Telegram Media Leecher: %s\n' "$*" >&2; exit 1; }

command -v docker >/dev/null 2>&1 || die "Docker is not installed. Install Docker Desktop or Docker Engine with Compose first."
docker compose version >/dev/null 2>&1 || die "Docker Compose v2 is required."
docker info >/dev/null 2>&1 || die "Docker is not running. Start Docker Desktop (or the Docker Engine) and retry."

umask 077
mkdir -p data
chmod 700 data

if [[ ! -f .env ]]; then
  printf 'Telegram Media Leecher — Guided Setup\n'
  printf 'Obtain your Telegram API credentials at https://my.telegram.org\n\n'

  read -r -p 'Telegram API ID (numeric): ' tg_api_id
  [[ "$tg_api_id" =~ ^[0-9]+$ ]] || die "Enter a valid numeric Telegram API ID."

  read -r -p 'Telegram API Hash (hexadecimal): ' tg_api_hash
  [[ "$tg_api_hash" =~ ^[0-9a-fA-F]{32}$ ]] || die "Enter a 32-character hexadecimal API hash."

  read -r -p 'Target chat / group name [Jellyfin]: ' target_chat
  if [[ -z "$target_chat" ]]; then target_chat="Jellyfin"; fi

  read -r -p 'Enable Jellyfin library refresh? (y/N): ' enable_jf
  jf_enabled="false"
  jf_url="http://localhost:8096"
  jf_key=""
  if [[ "$enable_jf" =~ ^[yY]([eE][sS])?$ ]]; then
    jf_enabled="true"
    read -r -p 'Jellyfin URL [http://localhost:8096]: ' jf_url_input
    if [[ -n "$jf_url_input" ]]; then jf_url="$jf_url_input"; fi
    read -rs -p 'Jellyfin API Key: ' jf_key
    printf '\n'
  fi

  {
    printf 'TG_API_ID=%s\n' "$tg_api_id"
    printf 'TG_API_HASH=%s\n' "$tg_api_hash"
    printf 'TG_SESSION_PATH=./data/telegram_session\n'
    printf 'TARGET_CHAT=%s\n' "$target_chat"
    printf 'DOWNLOAD_DIR_FILMS=/media/films\n'
    printf 'DOWNLOAD_DIR_SERIES=/media/series\n'
    printf 'DOWNLOAD_DIR_ANIMES=/media/animes\n'
    printf 'DOWNLOAD_DIR_ADULTE=/media/adulte\n'
    printf 'JELLYFIN_ENABLED=%s\n' "$jf_enabled"
    printf 'JELLYFIN_URL=%s\n' "$jf_url"
    printf 'JELLYFIN_API_KEY=%s\n' "$jf_key"
  } > .env
  chmod 600 .env
  unset tg_api_hash jf_key
else
  chmod 600 .env
  printf 'Using existing .env; no values were replaced.\n'
fi

docker compose config --quiet
docker compose build

if [[ ! -f ./data/telegram_session.session ]]; then
  printf '\n=== Telegram Authentication Required ===\n'
  printf 'Running one-time authentication. Please enter your phone number and verification code:\n'
  docker compose run --rm telegram-leecher python main.py || true
fi

docker compose up -d
docker compose ps
printf '\nTelegram Media Leecher is running!\n'
printf 'Follow logs with: docker compose logs -f telegram-leecher\n'
