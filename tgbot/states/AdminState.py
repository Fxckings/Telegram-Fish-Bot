from aiogram.dispatcher.filters.state import StatesGroup, State

class Admin(StatesGroup):
	main = State()

	accs = State()
	open_acc = State()
	delete_acc = State()
	acc_check_pass = State()
	acc_sign_in = State()

	check = State()
	check_result = State()

	statistic = State()

	export = State()
	export_new = State()
	export_old = State()
	export_all = State()