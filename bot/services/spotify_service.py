import logging
import tempfile
from pathlib import Path

import aiohttp
import spotipy
from spotipy.oauth2 import SpotifyOAuth

logger = logging.getLogger(__name__)


class SpotifyService:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, refresh_token: str):
        if not all([client_id, client_secret, redirect_uri, refresh_token]):
            raise ValueError("Spotify credentials and refresh token must be provided")
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.refresh_token = refresh_token

    async def get_current_playing(self):
        """Fetch the current playing track info from Spotify."""

        auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope="user-read-currently-playing",
            cache_path=None
        )
        auth_manager.refresh_token = self.refresh_token

        try:
            # Refresh token synchronously (spotipy is sync)
            token_info = auth_manager.refresh_access_token(self.refresh_token)
            sp = spotipy.Spotify(auth=token_info['access_token'])

            current = sp.current_user_playing_track()
            if not current or not current.get("item"):
                return None

            track = current["item"]
            images = track["album"]["images"]
            cover_url = images[0]["url"] if images else None

            song_info = {
                "song": track['name'],
                "artists": ', '.join(a['name'] for a in track['artists']),
                "album": track['album']['name'],
                "cover_url": cover_url
            }
            return song_info
        except Exception as e:
            logger.exception(f"SpotifyService: failed to get current playing track: {e}")
            raise

    async def download_cover_image(self, url: str) -> Path | None:
        """Download image from URL and return the temporary file Path."""
        if not url:
            return None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        logger.warning(f"SpotifyService: Failed to download cover image, status {resp.status}")
                        return None
                    image_bytes = await resp.read()
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                        tmp_file.write(image_bytes)
                        temp_path = Path(tmp_file.name)
                    return temp_path
        except Exception as e:
            logger.exception(f"SpotifyService: Exception during cover image download: {e}")
            return None
