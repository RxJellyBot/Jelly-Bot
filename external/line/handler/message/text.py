from JellyBot.sysconfig import System
from external.line import LineApiWrapper
from external.handle import EventObjectFactory, handle_main
from mongodb.factory import ExtraContentManager


def handle_text(event, destination):
    # FIXME: Discord handler
    #  REF 1: https://github.com/nick411077/repo_bot/blob/master/cogs/help.py
    #  REF 2: https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html

    # FIXME: [LP] Redirect to webpage if too long
    # FIXME: [LP] Handle over 5 messages
    handled_events = handle_main(EventObjectFactory.from_line(event))

    handle_main(EventObjectFactory.from_line(event)).get_contents_condition(
        lambda e: len(e.content) > System.MaxSendContentLength)

    LineApiWrapper.reply_text(
        event.reply_token,
        [txt_handled.content for txt_handled in handle_main(EventObjectFactory.from_line(event))])