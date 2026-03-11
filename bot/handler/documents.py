from aiogram import Router, F
from aiogram.types import Message, Document
from bot.tg_app import upload_document

router = Router()


@router.message(F.document)
async def handle_document(message: Message):
    doc: Document = message.document
    if not doc.file_name.endswith((".pdf", ".docx")):
        await message.answer("⚠️ Поддерживаются только PDF и DOCX файлы.")
        return

    await message.answer("⏳ Загружаю и обрабатываю документ...")
    try:
        file = await message.bot.get_file(doc.file_id)
        file_bytes = await message.bot.download_file(file.file_path)
        result = await upload_document(
            user_id=str(message.from_user.id),
            filename=doc.file_name,
            content_type=doc.mime_type,
            data=file_bytes.read(),
        )
        await message.answer(f"✅ Документ <b>{doc.file_name}</b> успешно загружен!")
    except Exception as e:
        await message.answer(f"❌ Ошибка при загрузке: {e}")