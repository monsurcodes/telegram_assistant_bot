from bot.core.assistant import AssistantBot
from bot.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    logger.info("Starting AssistantBot bot ...")
    bot = AssistantBot()
    bot.run()
    logger.info("AssistantBot stopped.")

if __name__ == "__main__":
    main()
