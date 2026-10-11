import os
import time
import logging
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
from .config import Config
from .organizer import route_media
from .notifier import trigger_jellyfin_refresh

logger = logging.getLogger("telegram_leecher.bot")

def extract_file_name(event) -> str:
    """Extracts the true filename from Telegram message attributes."""
    if hasattr(event.media, 'document') and event.media.document and event.media.document.attributes:
        for attr in event.media.document.attributes:
            if hasattr(attr, 'file_name') and attr.file_name:
                return attr.file_name

    # Fallback to message text or generic name
    raw_text = (event.raw_text or "").strip()
    if raw_text and not raw_text.startswith("/"):
        first_line = raw_text.splitlines()[0][:100]
        return first_line

    return "video_media.mkv"

def create_progress_bar(current: int, total: int, bar_length: int = 15) -> str:
    if total <= 0:
        return ""
    fraction = current / total
    filled_length = int(bar_length * fraction)
    bar = '█' * filled_length + '▒' * (bar_length - filled_length)
    percent = fraction * 100
    current_mb = current / (1024 * 1024)
    total_mb = total / (1024 * 1024)

    if total_mb >= 1024:
        current_gb = current_mb / 1024
        total_gb = total_mb / 1024
        return f"[{bar}] {percent:.1f}%\n📥 {current_gb:.2f} Go / {total_gb:.2f} Go"
    return f"[{bar}] {percent:.1f}%\n📥 {current_mb:.1f} Mo / {total_mb:.1f} Mo"

def setup_bot(config: Config) -> TelegramClient:
    """Initializes and returns the Telethon client with message handlers."""
    client = TelegramClient(config.session_path, config.api_id, config.api_hash)

    # Determine chat identifier (integer if numeric, string otherwise)
    chat_filter = int(config.target_chat) if config.target_chat.lstrip("-").isdigit() else config.target_chat

    @client.on(events.NewMessage(chats=chat_filter))
    async def message_handler(event):
        if not event.media:
            return

        file_name = extract_file_name(event)
        caption = event.raw_text or ""
        logger.info("New incoming media detected: '%s'", file_name)

        status_msg = await event.reply("⏳ **Analyse du fichier et préparation du téléchargement...**")

        dest_dir, meta = route_media(file_name, caption, config)
        title = meta["title"]
        media_type = meta["media_type"]
        season = meta.get("season")

        info_header = f"📁 **{title}**"
        if season:
            info_header += f" *(Saison {season})*"

        await status_msg.edit(f"⏳ **Téléchargement démarré...**\n{info_header}\n📂 Destination : `{dest_dir}`")

        last_edit_time = 0
        update_interval = 3.5  # Seconds between Telegram message edits (anti-flood)

        async def progress_callback(current, total):
            nonlocal last_edit_time
            now = time.time()
            if now - last_edit_time > update_interval:
                bar_text = create_progress_bar(current, total)
                status_text = f"⏳ **Téléchargement en cours...**\n{info_header}\n\n{bar_text}"
                try:
                    await status_msg.edit(status_text)
                    last_edit_time = now
                except FloodWaitError as e:
                    logger.warning("FloodWait of %s seconds encountered while updating progress.", e.seconds)
                    last_edit_time = now + e.seconds
                except Exception as ex:
                    logger.debug("Minor error updating progress message: %s", ex)

        try:
            downloaded_path = await event.download_media(file=dest_dir, progress_callback=progress_callback)
            if not downloaded_path:
                await status_msg.edit("❌ **Échec du téléchargement :** Aucun fichier sauvegardé.")
                return

            saved_name = os.path.basename(downloaded_path)
            logger.info("File successfully downloaded to %s", downloaded_path)

            jellyfin_text = ""
            if config.jellyfin_enabled:
                refreshed = trigger_jellyfin_refresh(config)
                jellyfin_text = "\n🍿 *Médiathèque Jellyfin actualisée avec succès.*" if refreshed else "\n⚠️ *Jellyfin n'a pas pu être actualisé.*"

            final_message = (
                f"✅ **Téléchargement terminé !**\n"
                f"🎬 Fichier : `{saved_name}`\n"
                f"📂 Rangé dans : `{dest_dir}`"
                f"{jellyfin_text}"
            )
            await status_msg.edit(final_message)

        except Exception as e:
            logger.exception("Error while downloading media: %s", e)
            try:
                await status_msg.edit(f"❌ **Erreur lors du téléchargement :**\n`{e}`")
            except Exception:
                pass

    return client
