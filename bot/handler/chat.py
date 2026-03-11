from aiogram import Router
from aiogram.types import Message

from bot.keyboards import animal_keyboard, main_menu_keyboard
from bot.tg_app import set_user_role, set_user_animal, ask
from backend.app.core.constants import ROLE_BUTTONS, ANIMAL_OPTIONS, ANIMAL_OPTIONS_TEXT, DIALOGUE_START, START_MESSAGE

router = Router()


@router.message(lambda m: m.text in ROLE_BUTTONS)
async def handle_role(message: Message):
    try:
        await set_user_role(str(message.from_user.id), message.text)
    except Exception as e:
        await message.answer(f"Ошибка установки роли: {e}")
        return
    await message.answer(ANIMAL_OPTIONS_TEXT, reply_markup=animal_keyboard())


@router.message(lambda m: m.text in ANIMAL_OPTIONS)
async def handle_animal(message: Message):
    try:
        await set_user_animal(str(message.from_user.id), message.text)
    except Exception as e:
        await message.answer(f"Ошибка установки животного: {e}")
        return
    await message.answer(DIALOGUE_START, reply_markup=main_menu_keyboard())


@router.message(lambda m: m.text == "🔄 Сменить роль")
async def change_role(message: Message):
    from bot.keyboards import role_keyboard
    await message.answer(START_MESSAGE, reply_markup=role_keyboard())


@router.message(lambda m: m.text == "🐄 Сменить животное")
async def change_animal(message: Message):
    await message.answer(ANIMAL_OPTIONS_TEXT, reply_markup=animal_keyboard())


@router.message(lambda m: m.text == "📂 Загрузить документ")
async def prompt_upload(message: Message):
    await message.answer("📎 Отправьте документ (PDF или DOCX) для загрузки в базу знаний.")


@router.message()
async def handle_query(message: Message):
    user_id = str(message.from_user.id)
    try:
        await ask(user_id, message.text, message.bot)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")