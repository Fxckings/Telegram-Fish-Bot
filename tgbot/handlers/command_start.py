from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from tgbot.dialogs.root import in_state
from tgbot.states.State import State
from tgbot.data.data import Data

from tgbot.services.Log import Log


async def welcome(message: Message, data: Data, state: FSMContext):
    if not await data.get_user(message.chat.id):
        await data.add_user(message.chat.id)
        await Log(message).enter_start()

    if (await data.get_user(message.chat.id))['session']:
        await State.menu.end.set()
    else:
        await State.menu.main.set()
    await in_state(
        state=state,
        message=message,
        repo=data,
        edit=False
    )

def register_command_start(dp: Dispatcher):
    dp.register_message_handler(welcome, commands=["start"], state='*')