from telethon import events

from bot.config import (
    SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI, SPOTIFY_REFRESH_TOKEN
)
from bot.core.base_plugin import BasePlugin
from bot.middleware.owner_check import owner_only
from bot.middleware.register_command_help import register_help_text
from bot.services.spotify_service import SpotifyService
from bot.utils.command_patterns import command_pattern
from bot.utils.logger import get_logger

logger = get_logger(__name__)


class SpotifyPlugin(BasePlugin):
    name = "Spotify"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.spotify_service = SpotifyService(
            SPOTIFY_CLIENT_ID,
            SPOTIFY_CLIENT_SECRET,
            SPOTIFY_REDIRECT_URI,
            SPOTIFY_REFRESH_TOKEN
        )

    def register(self):
        self.bot.dispatcher.register_handler(
            self.now_playing_handler,
            events.NewMessage(pattern=command_pattern("spotify"))
        )
        logger.info("SpotifyPlugin registered /spotify command")

    @owner_only
    @register_help_text(
        "/spotify",
        "Usage: /spotify - sends the current playing song from Spotify"
    )
    async def now_playing_handler(self, event: events.NewMessage.Event):
        user = await event.get_sender()
        logger.info(f"User {user.id} requested current Spotify song")

        try:
            song_info = await self.spotify_service.get_current_playing()
            if not song_info:
                await event.reply("No song is currently playing on your Spotify account.")
                logger.info(f"No currently playing song for user {user.id}")
                return

            caption = (
                f"🎵 **Now Playing on Spotify** 🎶\n\n"
                f"**🎤 Song:** {song_info['song']}\n"
                f"👩‍🎤 **Artist(s):** {song_info['artists']}\n"
                f"💿 **Album:** {song_info['album']}"
            )

            if song_info["cover_url"]:
                temp_path = await self.spotify_service.download_cover_image(song_info["cover_url"])
                if temp_path:
                    try:
                        await self.bot.client.send_file(
                            event.chat_id,
                            file=str(temp_path),
                            caption=caption,
                            force_document=False
                        )
                        return
                    finally:
                        if temp_path.exists():
                            temp_path.unlink()
                # Fallback if image download failed
                await event.reply(caption)
            else:
                await event.reply(caption)

            logger.info(f"Sent current Spotify song and cover to user {user.id}")
        except Exception as e:
            logger.exception(f"Failed to fetch Spotify song for user_id={user.id}: {e}")
            await event.reply(
                "Sorry, couldn't retrieve Spotify info. Reauthorize your Spotify account or check the logs."
            )
