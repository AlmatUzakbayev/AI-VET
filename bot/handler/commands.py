from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    from bot.tg_app import create_user
    from bot.keyboards import role_keyboard
    from backend.app.core.constants import START_MESSAGE
    await create_user(str(message.from_user.id))
    await message.answer(START_MESSAGE, reply_markup=role_keyboard())


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "🐾 <b>Ветеринарный ассистент</b>\n\n"
        "/start — начать диалог\n"
        "/upload — загрузить медицинный документ\n"
        "/help — эта справка"
    )


@router.message(Command("upload"))
async def cmd_upload(message: Message):
    await message.answer("📎 Отправьте документ (PDF или DOCX) для загрузки в базу знаний.")
