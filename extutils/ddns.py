"""
Module of utilities to update the IP address of an URL via DDNS.
"""
import os
import time
from threading import Thread

import requests

from extutils.logger import LoggerSkeleton

__all__ = ["activate_ddns_update"]

LOGGER = LoggerSkeleton("sys.ddnsupdate", logger_name_env="DDNS_UPDATE")

ENABLED = True
DDNS_PASSWORD = os.environ.get("DDNS_PASSWORD")
if not DDNS_PASSWORD:
    LOGGER.logger.error("DDNS_PASSWORD not found in environment variables.")
    ENABLED = False

DDNS_HOST = os.environ.get("DDNS_HOST")
if not DDNS_HOST:
    LOGGER.logger.error("DDNS_HOST not found in environment variables.")
    ENABLED = False

DDNS_DOMAIN = os.environ.get("DDNS_DOMAIN")
if not DDNS_DOMAIN:
    LOGGER.logger.error("DDNS_DOMAIN not found in environment variables.")
    ENABLED = False


def ddns_update(interval_sec: int, retry_sec: int = 60):
    """
    A blocking call to update the URL hosting IP via DDNS.

    :param interval_sec: DDNS updating interval
    :param retry_sec: time gap to retry upon failure
    """
    while True:
        try:
            requests.get(f"http://dynamicdns.park-your-domain.com/update?"
                         f"host={DDNS_HOST}&domain={DDNS_DOMAIN}&password={DDNS_PASSWORD}")
            LOGGER.logger.info("DDNS updated. Host: %s / Domain: %s", DDNS_HOST, DDNS_DOMAIN)
            time.sleep(interval_sec)
        except (requests.exceptions.ConnectionError, ConnectionRefusedError):
            LOGGER.logger.warning("Failed to update DDNS. ConnectionError. Retry in %d seconds.", retry_sec)
            time.sleep(retry_sec)


def activate_ddns_update(interval_sec: int, retry_sec: int = 60):
    """
    Start a :class:`Thread` to activate DDNS.

    Will print an error log and **NOT** raising any exceptions if any of the key environment variables is missing:

    - ``DDNS_PASSWORD``: Password for DDNS

    - ``DDNS_HOST``: Host of DDNS

    - ``DDNS_DOMAIN``: Domain of DDNS

    :param interval_sec: DDNS updating interval
    :param retry_sec: time gap to retry upon failure
    """
    if ENABLED:
        Thread(target=ddns_update, args=(interval_sec, retry_sec)).start()
    else:
        LOGGER.logger.error("DDNS update service cannot be started "
                            "because some necessary environment variables are not defined.")
