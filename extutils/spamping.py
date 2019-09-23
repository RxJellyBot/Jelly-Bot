import asyncio
import requests

from extutils.logger import LoggerSkeleton

__all__ = ["activate_ping_spam"]

logger = LoggerSkeleton("sys.pingspam", logger_name_env="PING_SPAM")


async def _spam_ping_(cd_sec):
    # Prevent from sleep
    while True:
        requests.get("http://bot-stage.raenonx.cc")
        requests.get("http://bot.raenonx.cc")
        logger.logger.info("Ping spammed.")
        await asyncio.sleep(cd_sec)


def activate_ping_spam(cd_sec: int):
    asyncio.ensure_future(_spam_ping_(cd_sec))
