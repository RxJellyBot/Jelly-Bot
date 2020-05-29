"""
Control related to the emoji on Discord.
"""


def get_emoji_url(emoji_id):
    """Get the image URL of an emoji."""
    return f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
