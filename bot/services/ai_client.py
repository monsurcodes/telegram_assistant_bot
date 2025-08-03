import logging

import google.generativeai as genai

from bot.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)


class GeminiAIClient:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable not set.")
        self.client = genai
        self.client.configure(api_key=self.api_key)

    async def ask(self, prompt: str) -> str:
        try:
            response = self.client.GenerativeModel(
                model_name="gemini-2.5-flash"
            ).generate_content(prompt)

            return getattr(response.text, "text", str(response.text))
        except Exception as e:
            logger.exception("Gemini API call failed")
            return "❌ Sorry, the AI service is temporarily unavailable."
