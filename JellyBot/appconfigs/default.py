import os
from django.apps import AppConfig


class JellyBotAppConfig(AppConfig):
    name = "JellyBot"

    def ready(self):
        from bot.event import signal_django_ready
        from extdiscord import run_server

        signal_django_ready()
        if os.environ.get("DISCORD_START"):
            run_server()
