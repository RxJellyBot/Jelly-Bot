import os
import sys


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
    from extdiscord.core import run_server

    run_server()


if __name__ == '__main__':
    # Prevent unnecessary execution of starting Discord Bot
    if sys.argv[1] == "runserver":
        discord_main()
    django_main()
