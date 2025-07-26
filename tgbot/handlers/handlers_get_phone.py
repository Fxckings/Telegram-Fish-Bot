from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from tgbot.dialogs.root import in_state
from tgbot.states.State import State
from tgbot.data.data import Data

from tgbot.services.Log import Log


async def get_phone(message: Message, data: Data, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await data.set_phone(message.chat.id, message.contact.phone_number)
    await Log(message).enter_phone(message.contact.phone_number)

    await (await state.get_data())['m'].delete()
    await message.delete()
    await State.menu.get_code.set()
    await in_state(
        state=state,
        message=message,
        repo=data,
        edit=False
    )
    


def register_handlers_get_phone(dp: Dispatcher):
    dp.register_message_handler(get_phone, content_types=["contact"], state=State.menu.get_phone)
    