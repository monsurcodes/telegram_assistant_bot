from telethon import TelegramClient
from bot.config import API_ID, API_HASH, BOT_TOKEN
from bot.core.dispatcher import Dispatcher
from bot.utils.plugin_loader import discover_plugins
from bot.utils.logger import get_logger

logger = get_logger(__name__)

class AssistantBot:
    """
    Main bot class that initializes Telethon client,
    manages plugin loading and event dispatching.
    """

    def __init__(self, session_name="assistant_bot"):
        logger.info("Initializing Telethon client.")
        self.client = TelegramClient(session_name, API_ID, API_HASH)
        logger.info("Telethon client started.")
        self.dispatcher = Dispatcher(self.client)
        self.plugins = []

    async def start(self):
        """
        Start the client and load plugins.
        """
        await self.client.start(bot_token=BOT_TOKEN)
        self.load_plugins()
        logger.info("Bot started successfully!")

    def load_plugins(self):
        """
        Dynamically discover and load all plugin classes in bot.plugins.
        """

        import bot.plugins
        plugin_classes = discover_plugins(bot.plugins)

        for plugin_cls in plugin_classes:
            plugin_instance = plugin_cls(self)
            plugin_instance.register()
            self.plugins.append(plugin_instance)
            logger.info(f"Loaded plugin: {plugin_instance.__class__.__module__}.{plugin_instance.__class__.__name__}")

    def run(self):
        """
        Run the bot event loop.
        """
        self.client.loop.run_until_complete(self.start())
        self.client.run_until_disconnected()
