from telethon import events

from bot.core.base_plugin import BasePlugin
from bot.middleware.register_command_help import register_help_text
from bot.services.ai_client import GeminiAIClient
from bot.utils.command_patterns import args_command_pattern
from bot.utils.logger import get_logger

logger = get_logger(__name__)


class AIChatPlugin(BasePlugin):
    name = "AIChat"

    def register(self):
        self.bot.dispatcher.register_handler(
            self.ask_command_handler,
            events.NewMessage(pattern=args_command_pattern("ask"))
        )
        logger.info("AIChatPlugin registered /ask command.")

    @register_help_text(
        "/ask <your question>",
        "Ask anything and get an AI-powered answer using Google Gemini!"
    )
    async def ask_command_handler(self, event: events.NewMessage.Event):
        query = event.pattern_match.group(1)
        if not query or not query.strip():
            await event.reply("❓ Please provide a question. Example: `/ask Tell me a joke`", parse_mode="md")
            return

        thinking_msg = await event.reply("🤖 Thinking...", parse_mode="md")

        ai_client = GeminiAIClient()
        response = await ai_client.ask(query.strip())

        if len(response) > 3500:
            response = response[:3500] + "..."

        await thinking_msg.edit(f"💡 **AI Answer:**\n\n{response}", parse_mode="md")
