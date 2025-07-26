import asyncio
import logging
from tgbot.services.Session import ImportSession

# Set up logging for debugging and monitoring
logger = logging.getLogger(__name__)

async def update_sign_in(bot):
    """
    Monitors sign-in codes for users in data._sign_in by checking the chat history
    of a specific chat ID (777000) and sends the code to the admin if new messages are found.

    Args:
        bot: The Telegram bot instance with configuration and methods.
    """
    config = bot.config
    data = config.data
    admin = config.admin

    while True:
        await asyncio.sleep(5)
        logger.info("Starting sign-in code monitoring cycle")

        try:
            # Iterate over a copy of keys to safely modify the dictionary
            for phone_number in list(data._sign_in.keys()):
                user_data = data._sign_in[phone_number]
                logger.debug(f"Processing user with phone {phone_number}")

                # Initialize the client session
                session_manager = ImportSession().inject(phone_number)
                client = session_manager.client

                try:
                    await client.connect()

                    # Retrieve chat history
                    # Note: Retrieving the entire chat history can be inefficient for chats with many messages.
                    # Consider optimizing by tracking message IDs or limiting retrieval.
                    messages = [m async for m in client.get_chat_history(777000)]
                    if messages:
                        code = messages[0].text  # Use the most recent message
                        count = len(messages)
                        logger.debug(f"Retrieved code: {code}, message count: {count}")

                        # Check if there are more messages than previously recorded
                        if count > user_data['count']:
                            await bot.send_message(admin, code)
                            await data.del_sign_in(phone_number)
                            logger.info(f"Sent code for user {phone_number} and removed from sign-in list")
                    else:
                        logger.debug(f"No messages found for user {phone_number}")

                except Exception as e:
                    logger.error(f"Error processing user {phone_number}: {e}")
                finally:
                    await client.disconnect()

        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")