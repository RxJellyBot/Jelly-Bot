from multiprocessing import Process

from django.apps import AppConfig

from extdiscord import run_server


def discord_main():
    run_server()


class JellyBotAppConfig(AppConfig):
    name = "JellyBot"

    def ready(self):
        Process(target=discord_main).start()
