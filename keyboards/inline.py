from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="☀️ Сегодня", callback_data="weather_today"),
            InlineKeyboardButton(text="📅 Неделя",  callback_data="weather_week"),
        ],
        [
            InlineKeyboardButton(text="📍 По геолокации", callback_data="weather_geo"),
            InlineKeyboardButton(text="🔔 Уведомления",  callback_data="notify_menu"),
        ],
        [
            InlineKeyboardButton(text="🏙 Сменить город", callback_data="change_city"),
        ],
    ])


def geo_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📍 Отправить геолокацию", request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def notify_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="07:00", callback_data="notify_07:00"),
            InlineKeyboardButton(text="08:00", callback_data="notify_08:00"),
            InlineKeyboardButton(text="09:00", callback_data="notify_09:00"),
        ],
        [
            InlineKeyboardButton(text="10:00", callback_data="notify_10:00"),
            InlineKeyboardButton(text="12:00", callback_data="notify_12:00"),
            InlineKeyboardButton(text="18:00", callback_data="notify_18:00"),
        ],
        [
            InlineKeyboardButton(text="❌ Отключить", callback_data="notify_off"),
            InlineKeyboardButton(text="◀️ Назад",     callback_data="back_main"),
        ],
    ])


def back_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
    ])
