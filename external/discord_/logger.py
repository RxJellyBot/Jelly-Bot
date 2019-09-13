from extutils.logger import LoggerSkeleton

__all__ = ["DISCORD", "DISCORD_INTERNAL"]


DISCORD = LoggerSkeleton("discord.sys", logger_name_env="DISCORD")
DISCORD_INTERNAL = LoggerSkeleton("discord", logger_name_env="DISCORD_INTERNAL")
