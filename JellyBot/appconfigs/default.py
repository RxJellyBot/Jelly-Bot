from django.apps import AppConfig

from bot.user import perform_existence_check
from msghandle import load_handling_functions


class JellyBotAppConfig(AppConfig):
    name = "JellyBot"

    def ready(self):
        load_handling_functions()
        perform_existence_check(set_name_to_cache=True)
