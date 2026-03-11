import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
import aiohttp

from backend.app.core.config import TELEGRAM_BOT_TOKEN, BACKEND_URL
from backend.app.core.constants import (
    CREATE_USER_ENDPOINT, SET_USER_ROLE_ENDPOINT,
    SET_USER_ANIMAL_ENDPOINT, ASK_ENDPOINT,
)


bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)


async def create_user(user_id: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BACKEND_URL}{CREATE_USER_ENDPOINT}",
            json={"user_id": user_id},
        ) as resp:
            if resp.status != 200:
                raise Exception(f"create_user failed: {resp.status}")
            return await resp.json()


async def set_user_role(user_id: str, role: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BACKEND_URL}{SET_USER_ROLE_ENDPOINT}",
            json={"user_id": user_id, "role": role},
        ) as resp:
            if resp.status != 200:
                raise Exception(f"set_user_role failed: {resp.status}")
            return await resp.json()


async def set_user_animal(user_id: str, animal: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BACKEND_URL}{SET_USER_ANIMAL_ENDPOINT}",
            json={"user_id": user_id, "animal": animal},
        ) as resp:
            if resp.status != 200:
                raise Exception(f"set_user_animal failed: {resp.status}")
            return await resp.json()


async def ask(user_id: str, user_text: str, tg_bot: Bot) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BACKEND_URL}{ASK_ENDPOINT}",
            json={"user_id": user_id, "user_text": user_text},
        ) as resp:
            if resp.status != 200:
                raise Exception(f"ask failed: {resp.status}")
            result = await resp.json()
            response_text: str = result["response"]

    await tg_bot.send_chat_action(user_id, "typing")
    delay = min(len(response_text) * 0.05, 3.0)
    await asyncio.sleep(delay)

    if len(response_text) > 2000:
        for part in response_text.split("\n\n"):
            if part.strip():
                await tg_bot.send_chat_action(user_id, "typing")
                await asyncio.sleep(1.0)
                await tg_bot.send_message(user_id, part.strip())
    else:
        await tg_bot.send_message(user_id, response_text)


async def upload_document(user_id: str, filename: str, content_type: str, data: bytes) -> dict:
    async with aiohttp.ClientSession() as session:
        form = aiohttp.FormData()
        form.add_field("user_id", user_id)
        form.add_field("file", data, filename=filename, content_type=content_type)
        async with session.post(
            f"{BACKEND_URL}/api/v1/ai-vet/documents/upload",
            data=form,
        ) as resp:
            if resp.status != 200:
                raise Exception(f"upload_document failed: {resp.status}")
            return await resp.json()


async def main() -> None:
    from bot.handler import commands, chat, documents as doc_handler

    await bot.delete_webhook(drop_pending_updates=True)

    dp = Dispatcher()
    dp.include_router(commands.router)
    dp.include_router(doc_handler.router)
    dp.include_router(chat.router)

    try:
        await dp.start_polling(bot, polling_timeout=5)
    except Exception as e:
        logging.error(f"Polling failed: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user.")
