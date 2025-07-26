from aiogram import types
from typing import List, Dict, Optional, NoReturn
from math import ceil

callbacks = {}

class Menu:

    args = [
        'name', 'callback', 'state',
        'url', 'view', 'selected',
        'answer', 'answer_type', 'if',
        'contact'
    ]

    def __init__(self):
        self.markup = types.InlineKeyboardMarkup()
        self.insert_button_state = None
        self.insert_list_state = None
        
        """
        name: text on button [str]
        callback: callback [str]
        state: migration <Migrate>
        url: migration to site [str]
        view: view button <condition>
        selected: view selected button <condition>
        answer: answer button click [str]
        answer_type: answer type [boolean]
        """



    async def add_inline_button(self, buttons: List[Dict]) -> NoReturn:

        # creating inline button and adding to list

        row = []
        for i in buttons:
            button = i
            args = button.keys()

            if 'view' in args:
                if not button['view']:
                    continue

            if 'selected' in args:
                if button['selected']:
                    button['name'] = f"· {button['name']} ·"

            if 'url' in args:
                row.append(types.InlineKeyboardButton(
                    button["name"], 
                    url=button["url"])
                )

            elif 'contact' in args:
                row.append()

            else:
                callback = 'callback' in args
                button['callback'] = button['callback'] if callback else button['state'].state
                row.append(types.InlineKeyboardButton(
                    button["name"], 
                    callback_data=button["callback"])
                )

            if 'state' in args:
                answer_text = False
                answer_type = False
                answer_if = None
                values = {}
                if 'answer' in args:
                    answer_text = button['answer']
                if 'answer_type' in args:
                    answer_type = button['answer_type']
                if 'if' in args:
                    answer_if = button['if']
                for key in args:
                    if key in self.args:
                        continue
                    values[key] = button[key]

                await self.add_callback(
                    callback=button["callback"], 
                    state=button["state"], 
                    answer={'text': answer_text, 'type': answer_type, 'if': answer_if}, 
                    values=values
                )
        await self.update_markup(*row)

    async def get_contact_button(self, text):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton(text, request_contact=True))
        return markup


    async def insert(self, state, name: str="‹ Назад") -> NoReturn:
        self.insert_button_state = state
        self.insert_button_name = name


    async def insert_list(self, state, list: List, segment: int, select_page: int):
        self.insert_list_state = state
        self.insert_list = list
        self.insert_list_segment = segment
        self.insert_select_page = select_page


    async def update_markup(self, *buttons) -> NoReturn:

        # adding buttons to markup

        self.markup.row(*buttons)


    async def get_markup(self) -> Optional[types.InlineKeyboardMarkup]:
        
        # return markup
        if not self.insert_list_state is None and self.insert_list:
            
            index = self.insert_list // self.insert_list_segment
            index = 1 if not index else index
            if index*self.insert_list_segment < self.insert_list:
                index += 1
            if index != 1:
                index_plus = ceil(self.insert_list / self.insert_list_segment)
                index = index_plus if index != index_plus else index
            page = self.insert_select_page
            lost = index - page

            btn = []
            buttons = [1, page, index]
            if page == 1:
                buttons.append(page+1)
                buttons.append(page+2)
                buttons.append(page+3)
            if page == 2:
                buttons.append(page+1)
                buttons.append(page+2)
            if page > 2:
                buttons.append(page-1)

            if lost == 1:
                buttons.append(page-2)
            if lost > 1:
                buttons.append(page+1)
            if not lost:
                buttons.append(page-2)
                buttons.append(page-3)

            buttons = list(set(buttons))
            buttons = sorted(buttons)
            for i in buttons:
                if i < 1 or i > index:
                    continue
                name = i
                if index > 5:
                    if page > 3:
                        if i == page-1 and lost > 2:
                            name = f"‹ {i}"
                        elif i == 1:
                            name = f"« {i}"
                    if lost > 2:
                        if index == i:
                            name = f"{i} »"
                        elif page+1 == i and i > 4:
                            name = f"{i} ›"
                button = {
                    'name': name,
                    'callback': f"{self.insert_list_state.state}_{i}",
                    'state': self.insert_list_state,
                    'selected': page == i,
                    'page': i
                }
                btn.append(button)
            await self.add_inline_button(btn)



        if not self.insert_button_state is None:
            await self.add_inline_button([
                {
                    'name': self.insert_button_name,
                    'callback': f'back_to_{self.insert_button_state.state}',
                    'state': self.insert_button_state
                }
            ])

        return self.markup


    async def add_callback(self, callback: str, state, answer, values) -> NoReturn:
        
        # adding callbacks to list

        if not callback in callbacks.keys():
            callbacks[callback] = {
                "state": state, 
                "answer": answer, 
                "values": values
            }


    async def update_callback(self, callback, state, repo):

        # catch click on button

        if callback.data in callbacks.keys():
            call = callbacks[callback.data]
            async with state.proxy() as data:
                for key in call['values'].keys():
                    data[key] = call['values'][key]

            if call['answer']['text'] and call['answer']['if'] is None:
                await callback.answer(
                    text=call['answer']['text'],
                    show_alert=call['answer']['type'])
            elif call['answer']['text'] and not call['answer']['if'] and not call['answer']['if'] is None:
                return await callback.answer(
                    text=call['answer']['text'],
                    show_alert=True)
            elif not call['answer']['text']:
                await callback.answer()

            await call['state'].set()
            from tgbot.dialogs.dialog import migrate
            
            callback.message.from_user = callback.from_user
            await migrate(
                state=state,
                message=callback.message,
                repo=repo,
                edit=True
            )

    
