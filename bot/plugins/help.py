import math

from telethon import events, Button

from bot.config import HELP_DISABLED_PLUGINS
from bot.core.base_plugin import BasePlugin
from bot.utils.command_patterns import args_command_pattern
from bot.utils.logger import get_logger

logger = get_logger(__name__)

PLUGINS_PER_PAGE = 9  # 3 rows x 3 buttons


def chunked(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


HELP_DISABLED_PLUGINS.extend(["HelpPlugin", "StartPlugin"])


class HelpPlugin(BasePlugin):

    def register(self):
        self.bot.dispatcher.register_handler(self.on_help_command,
                                             events.NewMessage(pattern=args_command_pattern("help")))
        self.bot.dispatcher.register_handler(self.on_help_callback, events.CallbackQuery)
        logger.info("HelpPlugin registered /help command")

    def get_plugin_instances(self):
        # Return all plugin instances except HelpPlugin itself
        return [p for p in self.bot.plugins if p.__class__.__name__ not in HELP_DISABLED_PLUGINS]

    def get_plugin_names(self):
        return [getattr(plugin, "name", plugin.__class__.__name__) for plugin in self.get_plugin_instances()]

    async def on_help_command(self, event):
        args = event.raw_text.strip().split(maxsplit=1)
        if len(args) == 1:
            # No arg, show main menu (page=0)
            await self.send_help_menu(event, page=0)
        else:
            # User requested /help <pluginname>
            plugin_name = args[1].strip()

            # Case-insensitive search for plugin
            logger.info(f"Help requested for plugin: '{plugin_name}'")

            plugin = next(
                (p for p in self.get_plugin_instances()
                 if getattr(p, "name", p.__class__.__name__).lower() == plugin_name.lower()),
                None
            )

            if not plugin:
                logger.warning(
                    f"Plugin '{plugin_name}' not found in loaded plugins: {[getattr(p, 'name', p.__class__.__name__) for p in self.bot.plugins]}")
                await event.respond(f"No plugin named '{plugin_name}' found.")
                return

            # Collect commands help using your decorator attributes
            help_lines = []
            for attr in dir(plugin):
                fn = getattr(plugin, attr)
                if callable(fn) and hasattr(fn, "__help_command__") and hasattr(fn, "__help_text__"):
                    help_lines.append(f"`{fn.__help_command__}` — {fn.__help_text__}")

            text = (
                    f"**Help for {getattr(plugin, 'name', plugin.__class__.__name__)}:**\n\n"
                    + ("\n".join(help_lines) if help_lines else "No documented commands for this plugin.")
            )
            await event.respond(text, parse_mode="md", link_preview=False)

    async def send_help_menu(self, event, page=0, update=False):
        plugin_names = self.get_plugin_names()
        total_plugins = len(plugin_names)
        total_pages = math.ceil(total_plugins / PLUGINS_PER_PAGE)
        page = page % total_pages if total_pages > 0 else 0
        start = page * PLUGINS_PER_PAGE
        end = start + PLUGINS_PER_PAGE
        plugins_on_page = plugin_names[start:end]

        button_rows = []
        for chunk in chunked(plugins_on_page, 3):
            row = [Button.inline(name, data=f"help_plugin:{name}:{page}") for name in chunk]
            button_rows.append(row)

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
            plugin = next((p for p in self.get_plugin_instances()
                           if getattr(p, "name", p.__class__.__name__) == plugin_name), None)

            if not plugin:
                await event.answer("Plugin not found!", alert=True)
                return

            help_lines = []
            for attr in dir(plugin):
                fn = getattr(plugin, attr)
                if callable(fn) and hasattr(fn, "__help_command__") and hasattr(fn, "__help_text__"):
                    help_lines.append(f"`{fn.__help_command__}` — {fn.__help_text__}")

            text = f"**Help for {plugin_name}:**\n\n" + (
                ("\n".join(help_lines)) if help_lines else "No documented commands for this plugin.")
            await event.edit(
                text,
                buttons=[
                    [Button.inline("🔙 Back", data=f"help_nav:menu:{page_str}")],
                    [Button.inline("❌ Close", data="help_nav:close")]
                ],
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
