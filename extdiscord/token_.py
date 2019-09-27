import os
import sys

__all__ = ["discord_token"]

discord_token = os.environ.get("DISCORD_TOKEN")
if not discord_token:
    print("Specify discord bot token as DISCORD_TOKEN in environment variables.")
    sys.exit(1)
