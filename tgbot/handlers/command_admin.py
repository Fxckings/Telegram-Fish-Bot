from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from tgbot.dialogs.root import in_state
from tgbot.states.State import State
from tgbot.data.data import Data

from tgbot.services.Log import Log


async def admin(message: Message, data: Data, state: FSMContext):
    await message.delete()
    if int(message.from_user.id) != message.bot.config.admin:
        return None

    await State.admin.main.set()
    await in_state(
        state=state,
        message=message,
        repo=data,
        edit=False
    )


async def check(message: Message, data: Data, state: FSMContext):
    await message.delete()
    await state.update_data(find=message.text)
    await State.admin.check_result.set()
    await in_state(
        state=state,
        message=message,
        repo=data,
        edit=False
    )

def register_command_admin(dp: Dispatcher):
    dp.register_message_handler(admin, commands=["a"], state='*')
    dp.register_message_handler(check, state=State.admin.check)