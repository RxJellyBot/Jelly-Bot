from django.conf import settings

from JellyBot.systemconfig import System
from bot.user import perform_existence_check
from bot.system import record_boot_dt
from extutils.ddns import activate_ddns_update
from msghandle import load_handling_functions


__all__ = ["signal_discord_ready", "signal_django_ready"]


_ready = {
    "Discord": False,
    "Django": False
}


def signal_django_ready():
    _ready["Discord"] = True
    _check_all_ready()


def signal_discord_ready():
    _ready["Django"] = True
    _check_all_ready()


def _check_all_ready():
    if all(_ready.values()):
        on_system_fully_ready()


def on_system_fully_ready():
    """Code to execute on system fully prepared."""
    load_handling_functions()
    record_boot_dt()

    if settings.PRODUCTION:
        perform_existence_check(set_name_to_cache=True)
        activate_ddns_update(System.DDNSUpdateIntervalSeconds)
