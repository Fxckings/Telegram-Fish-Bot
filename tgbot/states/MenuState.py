from aiogram.dispatcher.filters.state import StatesGroup, State

class Menu(StatesGroup):
	main = State()
	get_phone = State()
	get_code = State()
	update_code = State()
	_update_code = State()
	_update_code_back = State()
	get_session = State()
	error = State()
	error_code = State()
	end = State()

	