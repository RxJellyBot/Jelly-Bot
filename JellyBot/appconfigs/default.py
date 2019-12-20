from django.apps import AppConfig

from msghandle import load_handling_functions


class JellyBotAppConfig(AppConfig):
    name = "JellyBot"

    def ready(self):
        load_handling_functions()
