"""
Module which only contains the discord bot token.

Terminates the program if token not specified as ``DISCORD_TOKEN`` in environment variables.
"""
import os
import sys

from extutils.logger import SYSTEM


__all__ = ("discord_token",)

discord_token = os.environ.get("DISCORD_TOKEN")
if not discord_token:
    SYSTEM.logger.critical("Specify discord bot token as DISCORD_TOKEN in environment variables.")
    sys.exit(1)
