import tempfile
from pathlib import Path

import aiohttp
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from telethon import events

from bot.config import (
    SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI, SPOTIFY_REFRESH_TOKEN
)
from bot.core.base_plugin import BasePlugin
from bot.middleware.owner_check import owner_only
from bot.middleware.register_command_help import register_help_text
from bot.utils.command_patterns import command_pattern
from bot.utils.logger import get_logger

logger = get_logger(__name__)


class SpotifyPlugin(BasePlugin):
    name = "Spotify"

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
            sp = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=SPOTIFY_CLIENT_ID,
                    client_secret=SPOTIFY_CLIENT_SECRET,
                    redirect_uri=SPOTIFY_REDIRECT_URI,
                    scope="user-read-currently-playing",
                    cache_path=None
                )
            )
            # Set refresh token and get access token
            sp.auth_manager.refresh_token = SPOTIFY_REFRESH_TOKEN
            sp.auth_manager.get_access_token(as_dict=False)

            current = sp.current_user_playing_track()
            if current and current.get("item"):
                track = current["item"]
                images = track["album"]["images"]
                cover_url = images[0]["url"] if images else None

                caption = (
                    f"🎵 **Now Playing on Spotify** 🎶\n\n"
                    f"**🎤 Song:** {track['name']}\n"
                    f"👩‍🎤 **Artist(s):** {', '.join(a['name'] for a in track['artists'])}\n"
                    f"💿 **Album:** {track['album']['name']}"
                )

                if cover_url:
                    # Download the image and save temporarily
                    async with aiohttp.ClientSession() as session:
                        async with session.get(cover_url) as resp:
                            if resp.status == 200:
                                image_bytes = await resp.read()
                                # Use tempfile to create a temp jpg file
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                                    tmp_file.write(image_bytes)
                                    temp_path = Path(tmp_file.name)

                                try:
                                    await self.bot.client.send_file(
                                        event.chat_id,
                                        file=str(temp_path),
                                        caption=caption,
                                        force_document=False
                                    )
                                finally:
                                    # Cleanup temp file
                                    if temp_path.exists():
                                        temp_path.unlink()
                                return
                    # If downloading image failed
                    await event.respond(caption)
                else:
                    await event.respond(caption)

                logger.info(f"Sent current Spotify song and cover to user {user.id}")
            else:
                await event.respond("No song is currently playing on your Spotify account.")
                logger.info(f"No currently playing song for user {user.id}")
        except Exception as e:
            logger.exception(f"Failed to fetch Spotify song for user_id={user.id}: {e}")
            await event.respond(
                "Sorry, couldn't retrieve Spotify info. Reauthorize your Spotify account or check the logs.")
