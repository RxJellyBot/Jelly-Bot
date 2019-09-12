from external.line import LineApiWrapper


def handle_text(event, destination):
    print(f"[LINE] Received TextMessage to {destination}")
    # FIXME: [HP] Implement total handle and return all at once somewhere
    # FIXME: Add webhook/bot links on home page
    # FIXME: [MP] https://discordpy.readthedocs.io/en/latest/logging.html / LOGGER = logging.getLogger('linebot')
    # FIXME: Discord handler

    LineApiWrapper.reply_text(event.reply_token, event.message.text)
