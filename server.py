import os
import sys

import ray

from extdiscord import run_server

ray.init()


@ray.remote
def django_main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JellyBot.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


@ray.remote
def discord_main():
    run_server()


if __name__ == '__main__':
    ray.get([django_main.remote(), discord_main.remote()])
