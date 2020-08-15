"""Contains various functions for handling different type of message."""

from .text import handle_text
from .image import handle_image
from .sticker import handle_sticker
from .default import handle_msg_unhandled
from .main import handle_msg_main
