import tempfile
from pathlib import Path

import aiohttp

API = "https://meme-api.com/gimme/{subreddit}"


class RedditMemeService:
    @staticmethod
    async def fetch_meme(subreddit):
        url = API.format(subreddit=subreddit)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                return data if "url" in data else None

    @staticmethod
    async def download_image(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                img_bytes = await resp.read()
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                    tmp.write(img_bytes)
                    return Path(tmp.name)
