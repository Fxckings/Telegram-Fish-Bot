from tgbot.dialogs.dialog_menu import dialog_menu
from tgbot.dialogs.dialog_admin import dialog_admin
from tgbot.dialogs.dialog_admin_check import dialog_admin_check
from tgbot.dialogs.dialog_admin_statistic import dialog_admin_statistic
from tgbot.dialogs.dialog_admin_export import dialog_admin_export




async def in_state(state, repo, message, edit=True):
    current_state = await state.get_state()
    await dialog_menu(state, message, current_state, repo, edit)
    await dialog_admin(state, message, current_state, repo, edit)
    await dialog_admin_check(state, message, current_state, repo, edit)
    await dialog_admin_statistic(state, message, current_state, repo, edit)
    await dialog_admin_export(state, message, current_state, repo, edit)
    #print(await state.get_data())