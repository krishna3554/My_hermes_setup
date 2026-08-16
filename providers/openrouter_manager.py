import os
from dotenv import load_dotenv

load_dotenv()

class OpenRouterKeyManager:
    def __init__(self):
        self.keys = [
            os.getenv("OPENROUTER_API_KEY_1"),
            os.getenv("OPENROUTER_API_KEY_2"),
            os.getenv("OPENROUTER_API_KEY_3"),
        ]

        # Remove empty values
        self.keys = [k for k in self.keys if k]

        if not self.keys:
            raise ValueError("No OpenRouter API keys found.")

        self.current = 0

    def get_key(self):
        return self.keys[self.current]

    def rotate(self):
        self.current = (self.current + 1) % len(self.keys)
        return self.get_key()


_manager = None


def get_openrouter_key():
    """Return the active OpenRouter API key from the shared key manager."""
    global _manager
    if _manager is None:
        try:
            _manager = OpenRouterKeyManager()
        except ValueError:
            return ""
    return _manager.get_key()


def rotate_openrouter_key():
    """Rotate the shared OpenRouter key manager and return the new active key."""
    global _manager
    if _manager is None:
        try:
            _manager = OpenRouterKeyManager()
        except ValueError:
            return ""
    return _manager.rotate()
