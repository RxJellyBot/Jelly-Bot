from extutils.dt import now_utc_aware

boot_dt_utc = None


def record_boot_dt():
    global boot_dt_utc
    boot_dt_utc = now_utc_aware()
