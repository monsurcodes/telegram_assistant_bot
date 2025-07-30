from telethon import events

class Dispatcher:
    """
    Handles registration and dispatch of event handlers.
    Wraps addition of handlers to Telethon client for modularity.
    """

    def __init__(self, client):
        self.client = client

    def register_handler(self, handler, event_type=events.NewMessage):
        """
        Register a new event handler function.
        """
        self.client.add_event_handler(handler, event_type)
