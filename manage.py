import os
import sys
from threading import Thread

from extdiscord import run_server


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


def discord_main():
    run_server()


if __name__ == '__main__':
    Thread(target=django_main).start()
    Thread(target=discord_main).start()
