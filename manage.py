try:
    import uvloop

    uvloop.install()
except ImportError:
    pass


from telegram import TelegramClient, StopPropagation
from handlers import HANDLERS
from core import env
import models

from functools import wraps
import logging

logging.basicConfig(
    filename="debug.log",
    filemode="w",
    level=logging.WARNING,
    format="%(asctime)s :: %(levelname)-5s :: %(message)s",
)


def _stop_propagation(callback):
    @wraps(callback)
    async def _callback_wrapper(event):
        await callback(event)
        raise StopPropagation

    return _callback_wrapper


bot = TelegramClient(
    str(env.BASEDIR / "bot"),
    env.API_ID,
    env.API_HASH,
    flood_sleep_threshold=10,
    proxy=("socks5", "127.0.0.1", 12334)
)


for annonated in HANDLERS:
    for event in annonated.__metadata__:
        bot.add_event_handler(_stop_propagation(annonated.__origin__), event)


async def main():
    await models.initialize_database()

    bot.parse_mode = "html"

    print(
        "\r[*] Connecting (Telegram) | ( %d handlers )" % (len(HANDLERS)),
        end="",
    )
    await bot.start(bot_token=env.TOKEN)
    print(
        "\r[+] Bot Started Successfully | ( %d handlers ) | (username %s)"
        % (len(HANDLERS), bot.me.username)
    )

    await bot._run_until_disconnected()


try:
    bot.loop.run_until_complete(main())
except KeyboardInterrupt:
    print("Goodbye")
finally:
    bot.loop.run_until_complete(models.dispose_database())
