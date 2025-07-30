import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "123456"))
API_HASH = os.getenv("API_HASH", "your_api_hash_here")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")
OWNER_ID = int(os.getenv("OWNER_ID"))

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DBNAME = os.getenv("MONGODB_DBNAME", "telegram_assistant_bot")