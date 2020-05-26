"""
Markdown-related code from ``markdown2`` to be used in this bot.
"""
from markdown2 import Markdown


class CustomMarkdown(Markdown):
    """Hooking class to create a ``markdown2.Markdown``."""
    def preprocess(self, text):
        return text


markdown = CustomMarkdown(extras=["fenced-code-blocks"])
