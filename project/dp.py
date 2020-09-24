class Dispatcher:
    def __init__(self):
        self.handlers = {}

    def _register_handler(self, text, func):
        self.handlers[text] = func

    def message_handler(self, text: str):
        def decorator(func):
            self._register_handler(text, func)
        return decorator
