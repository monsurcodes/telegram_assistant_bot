import motor.motor_asyncio
from bot.config import MONGODB_URI, MONGODB_DBNAME

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
db = client[MONGODB_DBNAME]
