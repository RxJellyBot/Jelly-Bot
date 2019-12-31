from extutils.dt import now_utc_aware


__all__ = ["get_boot_dt", "record_boot_dt"]


boot_dt_utc = {"dt": None}


def get_boot_dt():
    return boot_dt_utc["dt"]


def record_boot_dt():
    boot_dt_utc["dt"] = now_utc_aware()
