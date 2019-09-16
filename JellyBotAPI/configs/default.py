from django.apps import AppConfig

from external.discord_ import run_server


class DefaultAppConfig(AppConfig):
    name = "JellyBotAPI"
    verbose_name = "Jelly Bot API"

    def ready(self):
        run_server()
