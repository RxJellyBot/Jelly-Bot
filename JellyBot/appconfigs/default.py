from django.apps import AppConfig

from bot.event import signal_django_ready


class JellyBotAppConfig(AppConfig):
    name = "JellyBot"

    def ready(self):
        signal_django_ready()
