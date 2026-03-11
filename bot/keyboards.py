from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from backend.app.core.constants import ROLE_BUTTONS, ANIMAL_OPTIONS


def role_keyboard() -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text=btn)] for btn in ROLE_BUTTONS]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def animal_keyboard() -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text=btn)] for btn in ANIMAL_OPTIONS]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="Задать вопрос")],
        [KeyboardButton(text="Загрузить документ")],
        [KeyboardButton(text="Сменить роль"), KeyboardButton(text="🐄 Сменить животное")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()