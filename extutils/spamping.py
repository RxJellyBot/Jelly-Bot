import asyncio
import requests

from JellyBot.systemconfig import HostUrl
from extutils.logger import LoggerSkeleton

__all__ = ["activate_ping_spam"]

logger = LoggerSkeleton("sys.pingspam", logger_name_env="PING_SPAM")


async def _spam_ping_(cd_sec):
    # Prevent from sleep
    while True:
        requests.get(HostUrl)
        logger.logger.info(f"Ping spammed to {HostUrl}")
        await asyncio.sleep(cd_sec)


def activate_ping_spam(cd_sec: int):
    asyncio.ensure_future(_spam_ping_(cd_sec))
