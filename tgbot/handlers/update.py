from tgbot.handlers.update_sessions import update_sessions
from tgbot.handlers.update_sign_in import update_sign_in
import asyncio


async def update(bot):
	await asyncio.gather(
		update_sessions(bot),
		update_sign_in(bot)
	)