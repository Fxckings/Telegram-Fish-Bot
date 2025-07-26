from random import choice


class gText:

	path = 'config/answer_text.txt'

	def __init__(self):
		with open(self.path) as file:
			self.file = [i for i in file.read().split('\n') if i != '' or not '#' in i]

	def get_dialog(self, dialog: str):
		lines = [i for i in self.file if dialog in i]
		self.title = lines[0].split(' *** ')[1]
		self.text = lines[1].split(' *** ')[1]
		self.image = lines[2].split(' *** ')[1]
		self.image = None if self.image == '0' else open(f"images/{self.image}", 'rb')
		return self

	def get(self, key: str):
		lines = [i for i in self.file if key in i]
		return lines[0].split(' *** ')[1]

	def error(self, error: str):
		with open(self.path) as file:
			lines = [i for i in self.file if 'ошибка' in i and error in i]
			return lines[0].split(' *** ')[1]


class gMeta:

	path = 'config/meta_sessions.txt'

	def __init__(self):
		with open(self.path) as file:
			self.file = [i for i in file.read().split('\n') if i != '' and not '#' in i]


	def get_random_meta(self):
		self.device_model = choice([i for i in self.file if 'модели_девайсов' in i][0].split(' *** ')[1].split(':'))
		self.system_version = choice([i for i in self.file if 'версии_систем' in i][0].split(' *** ')[1].split(':'))
		self.app_version = choice([i for i in self.file if 'версии_приложений' in i][0].split(' *** ')[1].split(':'))
		self.lang_code = choice([i for i in self.file if 'язык_пользователя' in i][0].split(' *** ')[1].split(':'))
		self.system_lang_code = choice([i for i in self.file if 'язык_системы' in i][0].split(' *** ')[1].split(':'))
		return self


class gProxy:

	path = 'config/proxy_sessions.txt'

	def __init__(self):
		with open(self.path) as file:
			self.file = [i for i in file.read().split('\n') if i != '' and not '#' in i]


	def random(self):
		if not len(self.file):
			return None

		select = choice(self.file).split(':')
		self.scheme = select[0]
		self.ip = select[1]
		self.port = select[2]
		self.login = select[3]
		self.password = select[4]
		return {
     		"scheme": self.scheme,
     		"hostname": self.ip,
     		"port": int(self.port),
     		"username": self.login,
     		"password": self.password
		}
