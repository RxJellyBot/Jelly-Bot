def handle_text(event, destination):
    # FIXME: [HP] Tests:
    #  Error occurred -> Email sent? Logged?
    # FIXME: Implement total handle and return all at once somewhere (Integrate text message first)
    # FIXME: Discord handler
    #  REF 1: https://github.com/nick411077/repo_bot/blob/master/cogs/help.py
    #  REF 2: https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html

    print(event.message.text)
