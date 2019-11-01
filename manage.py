import os
import sys
from multiprocessing import Process
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
    # FIXME: `RuntimeError: set_wakeup_fd only works in main thread` on Heroku (Ubuntu 18.03)
    # if sys.argv[1] == "runserver":
    #     Thread(target=discord_main).start()
    django_main()
