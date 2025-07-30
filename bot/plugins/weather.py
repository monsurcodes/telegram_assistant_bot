from telethon import events
from bot.core.base_plugin import BasePlugin
from bot.utils.command_patterns import args_command_pattern
from bot.config import WEATHERAPI_KEY
from bot.utils.logger import get_logger
import aiohttp

logger = get_logger(__name__)

class WeatherPlugin(BasePlugin):
    """
    Fetches current weather info for a given city using WeatherAPI.com.
    Command: /weather <city>
    """

    WEATHER_API_URL = "http://api.weatherapi.com/v1/current.json"

    def register(self):
        self.bot.dispatcher.register_handler(
            self.weather_handler,
            events.NewMessage(pattern=args_command_pattern("weather"))
        )
        logger.info("WeatherPlugin registered /weather command")

    async def weather_handler(self, event: events.NewMessage.Event):
        user = await event.get_sender()
        user_id = user.id if user else "unknown"
        city = event.pattern_match.group(1)

        if not city:
            logger.warning(f"User {user_id} sent /weather command without city argument")
            await event.respond("Please provide a city name. Example: /weather New York")
            return

        city = city.strip()
        logger.info(f"User {user_id} is fetching weather for city: {city}")

        if not WEATHERAPI_KEY:
            logger.error(f"User {user_id}: WeatherAPI.com API key is missing")
            await event.respond("Weather service is not configured properly. Contact the bot admin.")
            return

        params = {
            "key": WEATHERAPI_KEY,
            "q": city,
            "aqi": "no"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.WEATHER_API_URL, params=params) as resp:
                    if resp.status != 200:
                        logger.warning(
                            f"User {user_id}: Could not get weather data for '{city}', API response code {resp.status}")
                        await event.respond(f"Could not get weather data for '{city}'. Please check the city name.")
                        return
                    data = await resp.json()

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
            await event.respond(reply)
            logger.info(f"Sent weather info for city: {city} to user {user_id}")

        except Exception as e:
            logger.exception(f"User {user_id}: Failed fetching weather data: {e}")
            await event.respond("Sorry, something went wrong while fetching the weather data.")

