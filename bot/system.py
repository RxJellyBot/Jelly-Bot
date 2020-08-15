"""Functions to access systematic information."""
from datetime import datetime
from typing import Optional, Dict

from extutils.dt import now_utc_aware

__all__ = ("get_boot_dt", "record_boot_dt",)

boot_dt_utc: Dict[str, Optional[datetime]] = {"dt": None}


def get_boot_dt() -> Optional[datetime]:
    """
    Get the boot time of the application.

    :return: boot date time (tz-aware) of the application
    """
    return boot_dt_utc["dt"]


def record_boot_dt():
    """Record the boot time (tz-aware) of the application in UTC."""
    boot_dt_utc["dt"] = now_utc_aware()
