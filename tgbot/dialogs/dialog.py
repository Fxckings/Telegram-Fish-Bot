from aiogram.types import Message


async def dialog(message: Message, edit: bool=True, title: str='Title', text: str='Text', markup=None, image=False):
    try:  
        txt = '\n'.join(text)
        textmsg = f"<b>{title}</b>\n \n{txt}"

        if edit and not image:
            try:
                return await message.edit_text(
                    text=textmsg, reply_markup=markup, disable_web_page_preview=True
                )
            except:
                return await dialog(
                    message, edit=False, title=title,
                    text=text, markup=markup, image=image
                )
        
        try:
            await message.delete()
        except Exception:
            pass

        if image:
            return await message.answer_photo(
                photo=image, caption=textmsg, reply_markup=markup
            )

        return await message.answer(text=textmsg, reply_markup=markup, disable_web_page_preview=True)
    except Exception as e:
        print(e)
        return False


async def migrate(state, repo, message: Message, edit=True):
    from tgbot.dialogs.root import in_state
    return await in_state(state, repo, message, edit)