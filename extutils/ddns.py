import os
import time
from threading import Thread

import requests

from extutils.logger import LoggerSkeleton

__all__ = ["activate_ddns_update"]

logger = LoggerSkeleton("sys.ddnsupdate", logger_name_env="DDNS_UPDATE")

enabled = True
ddns_password = os.environ.get("DDNS_PASSWORD")
if not ddns_password:
    logger.logger.error("DDNS_PASSWORD not found in environment variables.")
    enabled = False

ddns_host = os.environ.get("DDNS_HOST")
if not ddns_host:
    logger.logger.error("DDNS_HOST not found in environment variables.")
    enabled = False

ddns_domain = os.environ.get("DDNS_DOMAIN")
if not ddns_domain:
    logger.logger.error("DDNS_DOMAIN not found in environment variables.")
    enabled = False


def ddns_update(interval_sec: int, retry_sec: int = 60):
    while True:
        try:
            requests.get(f"http://dynamicdns.park-your-domain.com/update?"
                         f"host={ddns_host}&domain={ddns_domain}&password={ddns_password}")
            logger.logger.info(f"DDNS updated. Host: {ddns_host} / Domain: {ddns_domain}")
            time.sleep(interval_sec)
        except (requests.exceptions.ConnectionError, ConnectionRefusedError):
            logger.logger.warning(f"Failed to update DDNS. ConnectionError. Retry in {retry_sec} seconds.")
            time.sleep(retry_sec)


def activate_ddns_update(interval_sec: int, retry_sec: int = 60):
    if enabled:
        Thread(target=ddns_update, args=(interval_sec, retry_sec)).start()
    else:
        logger.logger.error("DDNS update service cannot be started "
                            "because some necessary environment variables are not defined.")
