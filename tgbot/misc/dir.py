import os


def remove_session(session):
	path = f'sessions/{session}'
	try:
		os.remove(path + ".session")
		os.remove(path + ".json")
		return True
	except:
		return False