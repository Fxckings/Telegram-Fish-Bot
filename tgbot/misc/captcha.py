from random import choice


def captcha(lenght: int) -> str:
	abc = ''
	symbols = get_all_symbols()
	for i in range(lenght):
		a = choice(symbols)
		abc += str(a)
	return abc


def get_all_symbols():
	symbols = [i for i in range(10)]
	for i in "abcdefghijklmnopqrstuvwxyz":
		symbols.append(i)
		symbols.append(i.upper())
	symbols.append('_')
	return symbols