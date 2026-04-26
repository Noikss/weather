from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import get_user, upsert_user
from keyboards.inline import main_menu
from services.weather import get_coords

router = Router()


class CityState(StatesGroup):
    waiting_city = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await get_user(message.from_user.id)

    if user and user["city"]:
        await message.answer(
            f"👋 Привет, <b>{message.from_user.first_name}</b>!\n\n"
            f"📍 Текущий город: <b>{user['city']}</b>\n\n"
            f"Что показать?",
            parse_mode="HTML",
            reply_markup=main_menu()
        )
    else:
        await message.answer(
            f"👋 Привет, <b>{message.from_user.first_name}</b>!\n\n"
            f"Я покажу погоду в красивых карточках 🌤\n\n"
            f"Напиши название города чтобы начать:",
            parse_mode="HTML"
        )
        await state.set_state(CityState.waiting_city)


@router.message(CityState.waiting_city)
async def handle_city_input(message: Message, state: FSMContext):
    city_name = message.text.strip()
    result = await get_coords(city_name)

    if not result:
        await message.answer("❌ Город не найден. Попробуй ещё раз:")
        return

    lat, lon, name = result
    await upsert_user(message.from_user.id, city=name, lat=lat, lon=lon)
    await state.clear()

    await message.answer(
        f"✅ Город установлен: <b>{name}</b>\n\nЧто показать?",
        parse_mode="HTML",
        reply_markup=main_menu()
    )
