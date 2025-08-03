from telethon import events

from bot.config import WEATHERAPI_KEY
from bot.core.base_plugin import BasePlugin
from bot.middleware.register_command_help import register_help_text
from bot.services.weather_service import WeatherService
from bot.utils.command_patterns import args_command_pattern
from bot.utils.logger import get_logger

logger = get_logger(__name__)


class WeatherPlugin(BasePlugin):
    name = 'Weather'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.weather_service = WeatherService(WEATHERAPI_KEY)

    def register(self):
        self.bot.dispatcher.register_handler(
            self.weather_handler,
            events.NewMessage(pattern=args_command_pattern("weather"))
        )
        logger.info("WeatherPlugin registered /weather command")

    @register_help_text(
        '/weather <city>',
        "Show weather for given city.\nUsage: /weather New York"
    )
    async def weather_handler(self, event: events.NewMessage.Event):
        user = await event.get_sender()
        user_id = user.id if user else "unknown"
        city = event.pattern_match.group(1)

        if not city:
            logger.warning(f"User {user_id} sent /weather command without city argument")
            await event.reply("Please provide a city name. Example: /weather New York")
            return

        city = city.strip()
        logger.info(f"User {user_id} is fetching weather for city: {city}")

        if not WEATHERAPI_KEY:
            logger.error(f"User {user_id}: WeatherAPI.com API key is missing")
            await event.reply("Weather service is not configured properly. Contact the bot admin.")
            return

        reply = await self.weather_service.get_current_weather(city)
        if reply is None:
            await event.reply(f"Could not get weather data for '{city}'. Please check the city name.")
            return

        await event.reply(reply)
        logger.info(f"Sent weather info for city: {city} to user {user_id}")
