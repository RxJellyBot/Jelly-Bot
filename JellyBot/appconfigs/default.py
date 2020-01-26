from django.apps import AppConfig

from bot.event import signal_django_ready
from extdiscord import run_server


class JellyBotAppConfig(AppConfig):
    name = "JellyBot"

    def ready(self):
        signal_django_ready()
        run_server()
