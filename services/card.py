from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import math
from datetime import datetime

THEMES = {
    "clear":  {"top": (255, 180, 50),  "bot": (255, 100, 30),  "text": (255, 255, 255)},
    "clouds": {"top": (100, 120, 160), "bot": (60,  80,  120), "text": (255, 255, 255)},
    "rain":   {"top": (60,  90,  140), "bot": (30,  50,  100), "text": (200, 220, 255)},
    "snow":   {"top": (180, 210, 240), "bot": (120, 160, 210), "text": (255, 255, 255)},
    "storm":  {"top": (40,  40,  80),  "bot": (20,  20,  50),  "text": (180, 200, 255)},
    "mist":   {"top": (140, 150, 160), "bot": (90,  100, 120), "text": (240, 240, 255)},
    "default":{"top": (60,  100, 180), "bot": (20,  50,  120), "text": (255, 255, 255)},
}

DAY_NAMES = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


def get_theme(condition: str) -> dict:
    c = condition.lower()
    if "clear" in c:      return THEMES["clear"]
    if "rain" in c or "drizzle" in c: return THEMES["rain"]
    if "snow" in c:       return THEMES["snow"]
    if "storm" in c or "thunderstorm" in c: return THEMES["storm"]
    if "mist" in c or "fog" in c or "haze" in c: return THEMES["mist"]
    if "cloud" in c:      return THEMES["clouds"]
    return THEMES["default"]


def gradient_bg(draw, w, h, top, bot):
    for y in range(h):
        t = y / h
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        b = int(top[2] + (bot[2] - top[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def rounded_rect(draw, xy, radius, fill, alpha=180):
    x1, y1, x2, y2 = xy
    overlay = Image.new("RGBA", (x2 - x1, y2 - y1), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rounded_rectangle([0, 0, x2 - x1, y2 - y1], radius=radius, fill=(*fill[:3], alpha))
    return overlay, (x1, y1)


def try_font(size):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except:
        return ImageFont.load_default()


def try_font_regular(size):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()


def draw_weather_icon(img, cx, cy, code, size=44):
    d = ImageDraw.Draw(img)
    c = code[:2]
    r = size // 2

    sun_col   = (255, 220, 50)
    cloud_col = (220, 230, 245)
    rain_col  = (120, 170, 230)
    snow_col  = (210, 230, 255)
    bolt_col  = (255, 230, 0)

    def sun(x, y, rs, ray_len=10):
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1 = x + int((rs + 4) * math.cos(rad))
            y1 = y + int((rs + 4) * math.sin(rad))
            x2 = x + int((rs + ray_len) * math.cos(rad))
            y2 = y + int((rs + ray_len) * math.sin(rad))
            d.line([(x1, y1), (x2, y2)], fill=sun_col, width=2)
        d.ellipse([x-rs, y-rs, x+rs, y+rs], fill=sun_col)

    def cloud(x, y, w=36, h=16):
        d.ellipse([x-w, y-h, x+w, y+h], fill=cloud_col)
        d.ellipse([x-w//2-8, y-h*2, x+w//2+4, y], fill=cloud_col)
        d.ellipse([x+2, y-h*2+4, x+w-2, y], fill=cloud_col)

    def drops(x, y, n=3, offset_x=0):
        for i in range(n):
            dx = x + offset_x - (n-1)*7 + i*14
            d.ellipse([dx-3, y, dx+3, y+10], fill=rain_col)
            d.polygon([(dx, y), (dx-3, y+6), (dx+3, y+6)], fill=rain_col)

    def snowflakes(x, y, n=3, offset_x=0):
        for i in range(n):
            dx = x + offset_x - (n-1)*7 + i*14
            d.line([(dx, y+2), (dx, y+10)], fill=snow_col, width=2)
            d.line([(dx-4, y+6), (dx+4, y+6)], fill=snow_col, width=2)
            d.line([(dx-3, y+3), (dx+3, y+9)], fill=snow_col, width=1)
            d.line([(dx+3, y+3), (dx-3, y+9)], fill=snow_col, width=1)

    if c == "01":
        sun(cx, cy, r - 4)
    elif c == "02":
        sun(cx - r//2, cy - r//3, r//2, ray_len=6)
        cloud(cx + r//4, cy + r//4, w=28, h=12)
    elif c in ("03", "04"):
        cloud(cx, cy, w=36, h=16)
    elif c == "09":
        cloud(cx, cy - 10, w=32, h=13)
        drops(cx, cy + 12)
    elif c == "10":
        sun(cx - r//2, cy - r//2, r//2 - 2, ray_len=5)
        cloud(cx + 4, cy - 4, w=26, h=11)
        drops(cx + 4, cy + 14, n=2)
    elif c == "11":
        cloud(cx, cy - 12, w=32, h=13)
        drops(cx - 8, cy + 8, n=2)
        bolt = [(cx+6, cy+8), (cx, cy+20), (cx+5, cy+20), (cx-2, cy+34)]
        d.line(bolt, fill=bolt_col, width=3)
    elif c == "13":
        cloud(cx, cy - 10, w=32, h=13)
        snowflakes(cx, cy + 12)
    elif c == "50":
        for i in range(4):
            dy = cy - 12 + i * 9
            d.rounded_rectangle([cx - r + 4, dy, cx + r - 4, dy + 5], radius=2, fill=cloud_col)
    else:
        sun(cx, cy, r - 4)


def make_today_card(city: str, data: dict) -> BytesIO:
    W, H = 900, 500
    img = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(img)

    condition = data["weather"][0]["main"]
    desc = data["weather"][0]["description"].capitalize()
    theme = get_theme(condition)

    gradient_bg(draw, W, H, theme["top"], theme["bot"])

    # Декоративные круги
    for cx, cy, r, a in [(750, 80, 180, 20), (100, 400, 120, 15)]:
        circle = Image.new("RGBA", (r*2, r*2), (0,0,0,0))
        cd = ImageDraw.Draw(circle)
        cd.ellipse([0,0,r*2,r*2], fill=(255,255,255,a))
        img.paste(circle, (cx-r, cy-r), circle)

    tc = theme["text"]

    # Город
    f_city = try_font(52)
    draw.text((60, 50), city, font=f_city, fill=tc)

    # Дата
    f_date = try_font_regular(26)
    now = datetime.now()
    days_ru = ["Понедельник","Вторник","Среда","Четверг","Пятница","Суббота","Воскресенье"]
    months_ru = ["","Янв","Фев","Мар","Апр","Май","Июн","Июл","Авг","Сен","Окт","Ноя","Дек"]
    date_str = f"{days_ru[now.weekday()]}, {now.day} {months_ru[now.month]} {now.year}"
    draw.text((62, 115), date_str, font=f_date, fill=(*tc[:3], 200))

    # Иконка погоды большая
    icon_code = data["weather"][0]["icon"]
    draw_weather_icon(img, 430, 260, icon_code, size=90)

    # Температура
    temp = round(data["main"]["temp"])
    f_temp = try_font(160)
    draw.text((60, 150), f"{temp}°", font=f_temp, fill=tc)

    # Описание
    f_desc = try_font(34)
    draw.text((62, 330), desc, font=f_desc, fill=(*tc[:3], 220))

    # Блок деталей
    details = [
        ("Влажность", f"{data['main']['humidity']}%"),
        ("Ветер",     f"{round(data['wind']['speed'])} м/с"),
        ("Ощущается", f"{round(data['main']['feels_like'])}°C"),
        ("Видимость",  f"{data.get('visibility', 0) // 1000} км"),
    ]

    box_w, box_h = 185, 80
    start_x = 510
    for i, (label, val) in enumerate(details):
        bx = start_x + (i % 2) * (box_w + 16)
        by = 170 + (i // 2) * (box_h + 16)
        overlay, pos = rounded_rect(draw, (bx, by, bx+box_w, by+box_h), 16, (0,0,0), 60)
        img.paste(overlay, pos, overlay)
        fl = try_font_regular(18)
        fv = try_font(26)
        draw.text((bx+14, by+10), label, font=fl, fill=(*tc[:3], 180))
        draw.text((bx+14, by+36), val, font=fv, fill=tc)

    buf = BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf


def make_week_card(city: str, days: list) -> BytesIO:
    W, H = 900, 560
    img = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(img)

    condition = days[0]["condition"]
    theme = get_theme(condition)
    gradient_bg(draw, W, H, theme["top"], theme["bot"])

    tc = theme["text"]

    f_title = try_font(48)
    draw.text((60, 40), f"Прогноз  {city}", font=f_title, fill=tc)

    f_sub = try_font_regular(24)
    draw.text((62, 100), "На 7 дней", font=f_sub, fill=(*tc[:3], 180))

    card_w = 108
    gap = 14
    start_x = 40
    start_y = 155

    for i, day in enumerate(days[:7]):
        x = start_x + i * (card_w + gap)
        y = start_y
        ch = 340

        overlay, pos = rounded_rect(draw, (x, y, x+card_w, y+ch), 20, (0,0,0), 70)
        img.paste(overlay, pos, overlay)

        f_day = try_font(20)
        draw.text((x + card_w//2, y+14), day["day"], font=f_day, fill=tc, anchor="mt")

        f_date2 = try_font_regular(16)
        draw.text((x + card_w//2, y+42), day["date"], font=f_date2, fill=(*tc[:3], 180), anchor="mt")

        # Иконка нарисованная
        draw_weather_icon(img, x + card_w//2, y + 100, day["icon"], size=44)

        f_max = try_font(36)
        draw.text((x + card_w//2, y+148), f"{day['max']}°", font=f_max, fill=tc, anchor="mt")

        f_min = try_font_regular(26)
        draw.text((x + card_w//2, y+192), f"{day['min']}°", font=f_min, fill=(*tc[:3], 160), anchor="mt")

        f_hum = try_font_regular(16)
        draw.text((x + card_w//2, y+240), f"{day['humidity']}%", font=f_hum, fill=(*tc[:3], 200), anchor="mt")
        draw.text((x + card_w//2, y+262), f"{day['wind']}m/s", font=f_hum, fill=(*tc[:3], 200), anchor="mt")

        f_desc2 = try_font_regular(13)
        desc_short = day["desc"][:9]
        draw.text((x + card_w//2, y+292), desc_short, font=f_desc2, fill=(*tc[:3], 160), anchor="mt")

    buf = BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf
