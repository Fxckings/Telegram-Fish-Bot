from aiogram.types import CallbackQuery
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.services.MenuAPI import Menu
from tgbot.data.data import Data


async def update_callback(call : CallbackQuery, state: FSMContext, data: Data):
    calls = Menu()
    await calls.update_callback(call, state, data)
    

def register_update_callback(dp: Dispatcher):
    dp.register_callback_query_handler(update_callback, lambda call: True, state='*')