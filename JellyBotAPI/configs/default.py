from django.apps import AppConfig

from JellyBotAPI.sysconfig import System
from extutils import activate_ping_spam
from external.discord_ import run_server


class DefaultAppConfig(AppConfig):
    name = "JellyBotAPI"
    verbose_name = "Jelly Bot API"

    def ready(self):
        run_server()
        activate_ping_spam(System.PingSpamWaitSeconds)
