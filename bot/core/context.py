class Context:
    """
    Context object passed to handlers.
    Can hold user, chat, message info or any ephemeral state.
    """

    def __init__(self, event):
        self.event = event
        self.user = event.sender
        self.chat = event.chat
        self.message = event.message
