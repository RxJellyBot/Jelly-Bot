from django.utils.translation import activate, deactivate

from flags import Platform
from external.line import LineApiWrapper
from external.handle import EventObjectFactory, handle_main


def handle_text(request, event, destination):
    # FIXME: Discord handler
    #  REF 1: https://github.com/nick411077/repo_bot/blob/master/cogs/help.py
    #  REF 2: https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html

    activate('zh-tw')
    handled_events = handle_main(EventObjectFactory.from_line(event)).to_platform(request, Platform.LINE)
    handled_events.push_content()

    LineApiWrapper.reply_text(event.reply_token, handled_events.to_send)
    deactivate()
