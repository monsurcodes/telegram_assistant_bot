import aiohttp
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    WEATHER_API_URL = "http://api.weatherapi.com/v1/current.json"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("WeatherAPI key must be provided")
        self.api_key = api_key

    async def get_current_weather(self, city: str) -> str:
        """Fetch weather info for the given city and return a formatted string."""
        params = {
            "key": self.api_key,
            "q": city,
            "aqi": "no"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.WEATHER_API_URL, params=params) as resp:
                    if resp.status != 200:
                        logger.warning(f"Weather API returned status {resp.status} for city '{city}'")
                        return None
                    data = await resp.json()
        except Exception as e:
            logger.exception(f"Failed to fetch weather data for city '{city}': {e}")
            return None

        current = data.get("current", {})
        location = data.get("location", {})
        condition = current.get("condition", {})

        reply = (
            f"🌤 Weather in {location.get('name', city)}, {location.get('region', '')}:\n"
            f"{condition.get('text', '')}\n"
            f"Temperature: {current.get('temp_c', '?')}°C\n"
            f"Feels Like: {current.get('feelslike_c', '?')}°C\n"
            f"Humidity: {current.get('humidity', '?')}%\n"
            f"Wind Speed: {current.get('wind_kph', '?')} kph"
        )

        return reply
