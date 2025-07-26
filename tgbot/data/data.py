import json

class Data:

	def __init__(self):
		self.path = "tgbot/data/json/data.json"
		self.storage = {}
		self.sessions = {}
		self._sign_in = {}

	def load(self):
		with open(self.path) as file:
			self.storage = json.load(file)
			return self

	def save(self):
		with open(self.path, 'w') as file:
			json.dump(self.storage, file, indent=4)
			return True

	async def add_user(self, user_id):
		user_id = str(user_id)
		self.storage[user_id] = {
			"user_id": user_id,
			"phone": None,
			"session": None,
			"reset_auth": False,
			"export": False
		}
		return self.storage[user_id]

	async def get_user(self, user_id):
		user_id = str(user_id)
		if user_id in self.storage.keys():
			return self.storage[user_id]
		return False

	async def list_users(self):
		return self.storage

	async def list_users_of_sessions(self):
		result = []
		for i in self.storage.keys():
			if self.storage[i]['session']: result.append(self.storage[i])
		return result

	async def delete_user_of_phone(self, phone):
		for i in self.storage.keys():
			user = self.storage[i]
			if user['phone'] == phone:
				del self.storage[i]
				return True
		return False

	async def set_phone(self, user_id, phone):
		(await self.get_user(user_id))['phone'] = str(phone)

	async def select_session(self, user_id):
		phone = await self.get_phone(user_id)
		(await self.get_user(user_id))['session'] = f"sessions/{phone}"

	async def delete_select_session(self, user_id):
		(await self.get_user(user_id))['session'] = None
		self.save()

	async def get_phone(self, user_id):
		return (await self.get_user(user_id))['phone']

	async def reset_auth(self, user_id):
		(await self.get_user(user_id))['reset_auth'] = True
		self.save()

	async def sign_in(self, phone, count):
		self._sign_in[str(phone)] = {
			'phone': str(phone),
			'count': int(count)
		}

	async def del_sign_in(self, phone):
		if str(phone) in self._sign_in.keys():
			del self._sign_in[str(phone)]
			return True
		return False


	async def add_session(self, user_id, session):
		self.sessions[str(user_id)] = session

	async def get_session(self, user_id):
		if str(user_id) in self.sessions.keys():
			return self.sessions[str(user_id)]

	async def remove_session(self, user_id):
		if str(user_id) in self.sessions.keys():
			del self.sessions[str(user_id)]

	