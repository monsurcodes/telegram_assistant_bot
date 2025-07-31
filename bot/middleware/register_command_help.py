def register_help_text(command, help_text):
    def decorator(func):
        func.__help_command__ = command
        func.__help_text__ = help_text
        return func
    return decorator
