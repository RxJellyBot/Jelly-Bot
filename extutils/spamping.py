import time
from threading import Thread

import requests

from JellyBot.systemconfig import HostUrl
from extutils.logger import LoggerSkeleton

__all__ = ["activate_ping_spam"]

logger = LoggerSkeleton("sys.pingspam", logger_name_env="PING_SPAM")


def _spam_ping_(cd_sec: int, retry_sec: int = 60):
    # Prevent from sleep
    while True:
        try:
            requests.get(HostUrl)
            logger.logger.info(f"Ping spammed to {HostUrl}.")
            time.sleep(cd_sec)
        except (requests.exceptions.ConnectionError, ConnectionRefusedError):
            logger.logger.warning(f"Ping failed to spam on {HostUrl}. ConnectionError. Retry in {retry_sec} seconds.")
            time.sleep(retry_sec)


def activate_ping_spam(cd_sec: int, retry_sec: int = 60):
    Thread(target=_spam_ping_, args=(cd_sec, retry_sec)).start()
