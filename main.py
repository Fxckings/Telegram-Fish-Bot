import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from tgbot.config import load_config

from tgbot.handlers.update import update
from tgbot.middlewares.data import DataMiddleware
from tgbot.handlers.command_start import register_command_start
from tgbot.handlers.command_admin import register_command_admin
from tgbot.handlers.update_callback import register_update_callback
from tgbot.handlers.handlers_get_phone import register_handlers_get_phone




def register_all_middlewares(dp, data):
    dp.middleware.setup(DataMiddleware(data))


def register_all_handlers(dp):
    register_command_start(dp)
    register_command_admin(dp)
    register_update_callback(dp)
    register_handlers_get_phone(dp)
    
    
async def main():
    config = load_config('config/.env')

    storage = MemoryStorage()
    bot = Bot(token=config.bot.token, parse_mode=config.bot.parse_mode)
    dp = Dispatcher(bot, storage=storage)

    register_all_middlewares(dp, data=config.data)
    register_all_handlers(dp)
    bot.config = config

    try:
        print(f"Bot {config.bot.name} {config.bot.version} started!")
        await asyncio.gather(
            dp.start_polling(),
            update(bot)
        )
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print(f'Bot stopped!')