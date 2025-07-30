from abc import ABC, abstractmethod

class BasePlugin(ABC):
    """
    Abstract base class for all plugins.
    Plugins must inherit this and implement the register method to attach handlers.
    """

    def __init__(self, bot):
        self.bot = bot  # AssistantBot instance

    @abstractmethod
    def register(self):
        """
        Register plugin event handlers to the bot client.
        """
        pass
