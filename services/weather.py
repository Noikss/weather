import aiohttp
from config import OWM_API_KEY

BASE = "https://api.openweathermap.org/data/2.5"
GEO  = "https://api.openweathermap.org/geo/1.0"

WEATHER_ICONS = {
    "01": "☀️", "02": "🌤", "03": "☁️", "04": "☁️",
    "09": "🌧", "10": "🌦", "11": "⛈", "13": "❄️", "50": "🌫",
}

def icon(code: str) -> str:
    return WEATHER_ICONS.get(code[:2], "🌡")


async def get_coords(city: str):
    async with aiohttp.ClientSession() as s:
        r = await s.get(f"{GEO}/direct", params={"q": city, "limit": 1, "appid": OWM_API_KEY})
        data = await r.json()
        if not data:
            return None
        return data[0]["lat"], data[0]["lon"], data[0].get("local_names", {}).get("ru") or data[0]["name"]


async def get_coords_by_location(lat: float, lon: float):
    async with aiohttp.ClientSession() as s:
        r = await s.get(f"{GEO}/reverse", params={"lat": lat, "lon": lon, "limit": 1, "appid": OWM_API_KEY})
        data = await r.json()
        if not data:
            return None
        return data[0].get("local_names", {}).get("ru") or data[0]["name"]


async def get_current(lat: float, lon: float):
    async with aiohttp.ClientSession() as s:
        r = await s.get(f"{BASE}/weather", params={
            "lat": lat, "lon": lon, "appid": OWM_API_KEY,
            "units": "metric", "lang": "ru"
        })
        return await r.json()


async def get_forecast(lat: float, lon: float):
    async with aiohttp.ClientSession() as s:
        r = await s.get(f"{BASE}/forecast", params={
            "lat": lat, "lon": lon, "appid": OWM_API_KEY,
            "units": "metric", "lang": "ru", "cnt": 40
        })
        return await r.json()
