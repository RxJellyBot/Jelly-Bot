from external.line import LineApiWrapper
from external.handle import EventObjectFactory, handle_main


def handle_text(event, destination):
    # FIXME: Discord handler
    #  REF 1: https://github.com/nick411077/repo_bot/blob/master/cogs/help.py
    #  REF 2: https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html

    # FIXME: [LP] handle returned type will be changed
    LineApiWrapper.reply_text(event.reply_token, handle_main(EventObjectFactory.from_line(event)))
