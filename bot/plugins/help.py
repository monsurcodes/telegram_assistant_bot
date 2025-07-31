import math

from telethon import events, Button

from bot.core.base_plugin import BasePlugin
from bot.middleware.register_command_help import register_help_text
from bot.utils.command_patterns import command_pattern
from bot.utils.logger import get_logger

logger = get_logger(__name__)

# Number of plugins per help page:
PLUGINS_PER_PAGE = 9  # 3 rows x 3 buttons


def chunked(seq, n):
    """Yield successive n-sized chunks from seq."""
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


class HelpPlugin(BasePlugin):
    name = "Help"

    def register(self):
        self.bot.dispatcher.register_handler(self.on_help_command, events.NewMessage(pattern=command_pattern("help")))
        self.bot.dispatcher.register_handler(self.on_help_callback, events.CallbackQuery)
        logger.info("HelpPlugin registered /help command")

    def get_plugin_names(self):
        return [getattr(plugin, "name", plugin.__class__.__name__) for plugin in self.bot.plugins]

    @register_help_text(
        "/help",
        "Usage: /help - lists all available plugins with there help commands"
    )
    async def on_help_command(self, event):
        await self.send_help_menu(event, page=0)

    async def send_help_menu(self, event, page=0, update=False):
        # Prepare plugin name list and pagination
        plugin_names = self.get_plugin_names()
        total_plugins = len(plugin_names)
        total_pages = math.ceil(total_plugins / PLUGINS_PER_PAGE)
        page = page % total_pages
        start = page * PLUGINS_PER_PAGE
        end = start + PLUGINS_PER_PAGE
        plugins_on_page = plugin_names[start:end]

        # Group 3 per row
        button_rows = []
        for chunk in chunked(plugins_on_page, 3):
            row = [
                Button.inline(name, data=f"help_plugin:{name}:{page}")
                for name in chunk
            ]
            button_rows.append(row)

        # Nav buttons
        nav_buttons = []
        if total_pages > 1:
            nav_buttons.append(Button.inline("⬅️ Back", data=f"help_nav:back:{page}"))
        nav_buttons.append(Button.inline("❌ Close", data="help_nav:close"))
        if total_pages > 1:
            nav_buttons.append(Button.inline("Next ➡️", data=f"help_nav:next:{page}"))
        button_rows.append(nav_buttons)

        text = f"**Select a plugin below to see its commands:**\n\nPage {page + 1}/{total_pages}"
        if update:
            await event.edit(text, buttons=button_rows, parse_mode="md")
        else:
            await event.respond(text, buttons=button_rows, parse_mode="md", link_preview=False)

    async def on_help_callback(self, event):
        data = event.data.decode()
        if data.startswith("help_plugin:"):
            _, plugin_name, page_str = data.split(":")
            # Find the plugin instance
            plugin = next((p for p in self.bot.plugins
                           if getattr(p, "name", p.__class__.__name__) == plugin_name), None)

            # Only load commands with the decorator
            help_lines = []
            for attr in dir(plugin):
                fn = getattr(plugin, attr)
                if callable(fn) and hasattr(fn, "__help_command__") and hasattr(fn, "__help_text__"):
                    help_lines.append(
                        f"`{fn.__help_command__}` — {fn.__help_text__}"
                    )
            text = f"**Help for {plugin_name}:**\n\n" + (
                "\n".join(help_lines) if help_lines else "No documented commands for this plugin.")
            await event.edit(
                text,
                buttons=[[Button.inline("🔙 Back", data=f"help_nav:menu:{page_str}")],
                         [Button.inline("❌ Close", data="help_nav:close")]],
                parse_mode="md"
            )

        elif data.startswith("help_nav:"):
            parts = data.split(":")
            action = parts[1]
            page = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0

            plugin_names = self.get_plugin_names()
            total_plugins = len(plugin_names)
            total_pages = math.ceil(total_plugins / PLUGINS_PER_PAGE)
            if action == "back":
                await self.send_help_menu(event, page=(page - 1) % total_pages, update=True)
            elif action == "next":
                await self.send_help_menu(event, page=(page + 1) % total_pages, update=True)
            elif action == "menu":
                await self.send_help_menu(event, page=page, update=True)
            elif action == "close":
                await event.delete()
