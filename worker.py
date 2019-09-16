import asyncio

import requests

from external.discord_ import start_discord_client_non_block


async def _spam_ping_():
    # Prevent from sleep
    while True:
        requests.get("http://bot-stage.raenonx.cc")
        requests.get("http://bot.raenonx.cc")
        await asyncio.sleep(1740)


if __name__ == '__main__':
    asyncio.ensure_future(_spam_ping_())
    # start_client()
