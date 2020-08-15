"""Markdown-related code from ``markdown2`` to be used in this bot."""
from markdown2 import Markdown


class CustomMarkdown(Markdown):
    """Hooking class to create a ``markdown2.Markdown``."""


markdown = CustomMarkdown(extras=["fenced-code-blocks"])
