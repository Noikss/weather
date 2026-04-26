from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from collections import defaultdict
from datetime import datetime

from database.db import get_user, upsert_user, set_notify
from keyboards.inline import main_menu, geo_keyboard, notify_menu, back_main
from services.weather import get_coords, get_coords_by_location, get_current, get_forecast
from services.card import make_today_card, make_week_card

router = Router()


class ChangeCityState(StatesGroup):
    waiting_city = State()


def parse_forecast(data: dict) -> list:
    days = defaultdict(lambda: {"temps": [], "icons": [], "humidity": [], "wind": [], "descs": []})
    for item in data["list"]:
        date = item["dt_txt"][:10]
        days[date]["temps"].append(item["main"]["temp"])
        days[date]["icons"].append(item["weather"][0]["icon"])
        days[date]["humidity"].append(item["main"]["humidity"])
        days[date]["wind"].append(item["wind"]["speed"])
        days[date]["descs"].append(item["weather"][0]["description"])
        days[date]["condition"] = item["weather"][0]["main"]

    result = []
    for date_str, d in list(days.items())[:7]:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        result.append({
            "day": ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"][dt.weekday()],
            "date": dt.strftime("%d.%m"),
            "max": round(max(d["temps"])),
            "min": round(min(d["temps"])),
            "icon": max(set(d["icons"]), key=d["icons"].count),
            "humidity": round(sum(d["humidity"]) / len(d["humidity"])),
            "wind": round(sum(d["wind"]) / len(d["wind"])),
            "desc": max(set(d["descs"]), key=d["descs"].count).capitalize(),
            "condition": d["condition"],
        })
    return result


async def send_today(bot: Bot, chat_id: int, user):
    current = await get_current(user["lat"], user["lon"])
    card = make_today_card(user["city"], current)
    photo = BufferedInputFile(card.read(), filename="weather.jpg")
    temp = round(current["main"]["temp"])
    desc = current["weather"][0]["description"].capitalize()
    await bot.send_photo(
        chat_id, photo,
        caption=f"☀️ <b>{user['city']}</b> • Сейчас\n{desc}, <b>{temp}°C</b>",
        parse_mode="HTML",
        reply_markup=main_menu()
    )


async def send_week(bot: Bot, chat_id: int, user):
    forecast = await get_forecast(user["lat"], user["lon"])
    days = parse_forecast(forecast)
    card = make_week_card(user["city"], days)
    photo = BufferedInputFile(card.read(), filename="weather_week.jpg")
    await bot.send_photo(
        chat_id, photo,
        caption=f"📅 <b>{user['city']}</b> • Прогноз на неделю",
        parse_mode="HTML",
        reply_markup=main_menu()
    )


# --- Callbacks ---

@router.callback_query(F.data == "weather_today")
async def cb_today(call: CallbackQuery, bot: Bot):
    user = await get_user(call.from_user.id)
    if not user or not user["lat"]:
        await call.answer("Сначала укажи город!", show_alert=True)
        return
    await call.answer()
    await call.message.answer("⏳ Загружаю...")
    await send_today(bot, call.message.chat.id, user)


@router.callback_query(F.data == "weather_week")
async def cb_week(call: CallbackQuery, bot: Bot):
    user = await get_user(call.from_user.id)
    if not user or not user["lat"]:
        await call.answer("Сначала укажи город!", show_alert=True)
        return
    await call.answer()
    await call.message.answer("⏳ Загружаю...")
    await send_week(bot, call.message.chat.id, user)


@router.callback_query(F.data == "weather_geo")
async def cb_geo(call: CallbackQuery):
    await call.answer()
    await call.message.answer(
        "📍 Отправь свою геолокацию:",
        reply_markup=geo_keyboard()
    )


@router.message(F.location)
async def handle_location(message: Message, bot: Bot):
    lat = message.location.latitude
    lon = message.location.longitude
    city = await get_coords_by_location(lat, lon)
    if not city:
        city = "Твоё местоположение"
    await upsert_user(message.from_user.id, city=city, lat=lat, lon=lon)
    user = await get_user(message.from_user.id)
    await message.answer(f"✅ Определил: <b>{city}</b>", parse_mode="HTML")
    await message.answer("⏳ Загружаю...")
    await send_today(bot, message.chat.id, user)


@router.callback_query(F.data == "change_city")
async def cb_change_city(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("🏙 Напиши название города:")
    await state.set_state(ChangeCityState.waiting_city)


@router.message(ChangeCityState.waiting_city)
async def handle_new_city(message: Message, state: FSMContext, bot: Bot):
    result = await get_coords(message.text.strip())
    if not result:
        await message.answer("❌ Город не найден. Попробуй ещё раз:")
        return
    lat, lon, name = result
    await upsert_user(message.from_user.id, city=name, lat=lat, lon=lon)
    await state.clear()
    user = await get_user(message.from_user.id)
    await message.answer(f"✅ Город изменён: <b>{name}</b>", parse_mode="HTML")
    await send_today(bot, message.chat.id, user)


@router.callback_query(F.data == "notify_menu")
async def cb_notify_menu(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        "🔔 Выбери время для ежедневного уведомления с погодой:",
        reply_markup=notify_menu()
    )


@router.callback_query(F.data.startswith("notify_"))
async def cb_notify_set(call: CallbackQuery):
    val = call.data.replace("notify_", "")
    if val == "off":
        await set_notify(call.from_user.id, None)
        await call.answer("🔕 Уведомления отключены", show_alert=True)
    else:
        await set_notify(call.from_user.id, val)
        await call.answer(f"✅ Уведомления в {val}", show_alert=True)
    await call.message.edit_text("Что показать?", reply_markup=main_menu())


@router.callback_query(F.data == "back_main")
async def cb_back(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text("Что показать?", reply_markup=main_menu())
