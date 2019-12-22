from django.apps import AppConfig

from msghandle import load_handling_functions
from models import load_user_name_cache


class JellyBotAppConfig(AppConfig):
    name = "JellyBot"

    def ready(self):
        load_handling_functions()
        load_user_name_cache()
