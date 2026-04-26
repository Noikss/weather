from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import math
from datetime import datetime

# iPhone-style themes
THEMES = {
    "clear_day":  {"top": (255, 200, 60),  "bot": (255, 120, 30),  "text": (255,255,255), "card": (255,160,40,80)},
    "clear_night":{"top": (30,  40,  100), "bot": (10,  15,  60),  "text": (255,255,255), "card": (50,60,120,80)},
    "clouds":     {"top": (120, 140, 180), "bot": (70,  90,  140), "text": (255,255,255), "card": (100,120,160,80)},
    "rain":       {"top": (50,  90,  160), "bot": (20,  50,  110), "text": (220,235,255), "card": (60,90,150,80)},
    "snow":       {"top": (170, 200, 240), "bot": (100, 140, 210), "text": (255,255,255), "card": (150,180,230,80)},
    "storm":      {"top": (35,  35,  75),  "bot": (15,  15,  45),  "text": (200,215,255), "card": (50,50,100,80)},
    "mist":       {"top": (150, 160, 175), "bot": (100, 110, 130), "text": (245,245,255), "card": (130,140,160,80)},
    "default":    {"top": (50,  100, 200), "bot": (20,  60,  150), "text": (255,255,255), "card": (60,90,180,80)},
}

MONTHS_RU = ["","Янв","Фев","Мар","Апр","Май","Июн","Июл","Авг","Сен","Окт","Ноя","Дек"]
DAYS_RU   = ["Понедельник","Вторник","Среда","Четверг","Пятница","Суббота","Воскресенье"]
DAYS_SHORT = ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]


def get_theme(condition: str, icon: str = "01d") -> dict:
    c = condition.lower()
    night = icon.endswith("n")
    if "clear" in c:
        return THEMES["clear_night"] if night else THEMES["clear_day"]
    if "rain" in c or "drizzle" in c: return THEMES["rain"]
    if "snow" in c:       return THEMES["snow"]
    if "thunderstorm" in c: return THEMES["storm"]
    if "mist" in c or "fog" in c or "haze" in c: return THEMES["mist"]
    if "cloud" in c:      return THEMES["clouds"]
    return THEMES["default"]


def gradient_bg(img, w, h, top, bot):
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(top[0] + (bot[0]-top[0])*t)
        g = int(top[1] + (bot[1]-top[1])*t)
        b = int(top[2] + (bot[2]-top[2])*t)
        draw.line([(0,y),(w,y)], fill=(r,g,b))


def glass_rect(img, x1, y1, x2, y2, radius=20, fill_color=(255,255,255,40), border=True):
    overlay = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(overlay)
    d.rounded_rectangle([x1,y1,x2,y2], radius=radius, fill=fill_color)
    if border:
        d.rounded_rectangle([x1,y1,x2,y2], radius=radius, outline=(255,255,255,60), width=1)
    img = Image.alpha_composite(img, overlay)
    return img


def font_bold(size):
    for path in [
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]:
        try: return ImageFont.truetype(path, size)
        except: pass
    return ImageFont.load_default()


def font_reg(size):
    for path in [
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        try: return ImageFont.truetype(path, size)
        except: pass
    return ImageFont.load_default()


def draw_icon(img, cx, cy, code, size=50):
    d = ImageDraw.Draw(img)
    c = code[:2]
    r = size // 2
    sun  = (255, 220, 50)
    cld  = (225, 235, 248)
    rain = (100, 160, 220)
    snow = (200, 225, 255)
    bolt = (255, 230, 0)

    def _sun(x, y, rs, rays=8, ray_len=10):
        for i in range(rays):
            a = math.radians(i * 360 / rays)
            x1 = x + int((rs+4)*math.cos(a)); y1 = y + int((rs+4)*math.sin(a))
            x2 = x + int((rs+ray_len)*math.cos(a)); y2 = y + int((rs+ray_len)*math.sin(a))
            d.line([(x1,y1),(x2,y2)], fill=sun, width=2)
        d.ellipse([x-rs,y-rs,x+rs,y+rs], fill=sun)

    def _cloud(x, y, w=40, h=18):
        d.ellipse([x-w,y-h,x+w,y+h], fill=cld)
        d.ellipse([x-w//2-6,y-h*2+2,x+w//2,y+2], fill=cld)
        d.ellipse([x+2,y-h*2+6,x+w-4,y+2], fill=cld)

    def _drops(x, y, n=3, dx=0):
        for i in range(n):
            px = x + dx - (n-1)*8 + i*16
            pts = [(px,y),(px-4,y+12),(px+4,y+12)]
            d.polygon(pts, fill=rain)
            d.ellipse([px-4,y,px+4,y+8], fill=rain)

    def _snow(x, y, n=3, dx=0):
        for i in range(n):
            px = x + dx - (n-1)*8 + i*16
            d.line([(px,y+2),(px,y+12)], fill=snow, width=2)
            d.line([(px-5,y+7),(px+5,y+7)], fill=snow, width=2)
            d.line([(px-4,y+3),(px+4,y+11)], fill=snow, width=1)
            d.line([(px+4,y+3),(px-4,y+11)], fill=snow, width=1)

    if c == "01":
        _sun(cx, cy, r-4)
    elif c == "02":
        _sun(cx-r//2, cy-r//3, r//2, rays=8, ray_len=6)
        _cloud(cx+r//4, cy+r//4, w=r-4, h=r//2-2)
    elif c in ("03","04"):
        _cloud(cx, cy, w=r+4, h=r//2+2)
    elif c == "09":
        _cloud(cx, cy-12, w=r+2, h=r//2)
        _drops(cx, cy+14)
    elif c == "10":
        _sun(cx-r//2, cy-r//2, r//3, ray_len=5)
        _cloud(cx+r//4, cy-r//4, w=r-2, h=r//2-2)
        _drops(cx+r//4, cy+16, n=2)
    elif c == "11":
        _cloud(cx, cy-14, w=r+2, h=r//2)
        _drops(cx-10, cy+10, n=2)
        bolt_pts = [(cx+8,cy+8),(cx+1,cy+22),(cx+7,cy+22),(cx-2,cy+38)]
        d.line(bolt_pts, fill=bolt, width=3)
    elif c == "13":
        _cloud(cx, cy-12, w=r+2, h=r//2)
        _snow(cx, cy+14)
    elif c == "50":
        for i in range(4):
            dy = cy - 14 + i*10
            d.rounded_rectangle([cx-r+6, dy, cx+r-6, dy+5], radius=3, fill=cld)
    else:
        _sun(cx, cy, r-4)


def make_today_card(city: str, data: dict) -> BytesIO:
    W, H = 900, 480
    img = Image.new("RGBA", (W, H))

    condition = data["weather"][0]["main"]
    icon_code = data["weather"][0]["icon"]
    desc = data["weather"][0]["description"].capitalize()
    theme = get_theme(condition, icon_code)

    gradient_bg(img, W, H, theme["top"], theme["bot"])

    # Большой декоративный круг
    circle = Image.new("RGBA", (W, H), (0,0,0,0))
    cd = ImageDraw.Draw(circle)
    cd.ellipse([W-350, -150, W+150, 350], fill=(255,255,255,18))
    cd.ellipse([-100, H-200, 250, H+100], fill=(255,255,255,12))
    img = Image.alpha_composite(img, circle)

    draw = ImageDraw.Draw(img)
    tc = theme["text"]

    # Название города
    draw.text((60, 48), city, font=font_bold(54), fill=tc)

    # Дата
    now = datetime.now()
    date_str = f"{DAYS_RU[now.weekday()]}, {now.day} {MONTHS_RU[now.month]} {now.year}"
    draw.text((62, 112), date_str, font=font_reg(26), fill=(*tc[:3], 190))

    # Большая температура
    temp = round(data["main"]["temp"])
    draw.text((60, 155), f"{temp}°", font=font_bold(170), fill=tc)

    # Описание
    draw.text((64, 348), desc, font=font_bold(32), fill=(*tc[:3], 220))

    # Большая иконка
    draw_icon(img, 680, 210, icon_code, size=110)

    # Детали — glassmorphism карточки
    details = [
        ("Влажность",  f"{data['main']['humidity']}%"),
        ("Ветер",      f"{round(data['wind']['speed'])} м/с"),
        ("Ощущается",  f"{round(data['main']['feels_like'])}°"),
        ("Видимость",  f"{data.get('visibility',0)//1000} км"),
    ]
    bw, bh, gap = 190, 82, 14
    sx = 60
    by_start = 390
    for i, (label, val) in enumerate(details):
        bx = sx + i*(bw+gap)
        img = glass_rect(img, bx, by_start, bx+bw, by_start+bh, radius=18,
                         fill_color=(255,255,255,35))
        draw = ImageDraw.Draw(img)
        draw.text((bx+14, by_start+10), label, font=font_reg(17), fill=(*tc[:3],170))
        draw.text((bx+14, by_start+34), val,   font=font_bold(26), fill=tc)

    buf = BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=95)
    buf.seek(0)
    return buf


def make_week_card(city: str, days: list) -> BytesIO:
    W, H = 920, 580
    img = Image.new("RGBA", (W, H))

    condition = days[0]["condition"]
    icon_code = days[0]["icon"]
    theme = get_theme(condition, icon_code)
    gradient_bg(img, W, H, theme["top"], theme["bot"])

    # Декор
    circle = Image.new("RGBA", (W,H), (0,0,0,0))
    cd = ImageDraw.Draw(circle)
    cd.ellipse([W-300,-100,W+200,400], fill=(255,255,255,15))
    img = Image.alpha_composite(img, circle)

    draw = ImageDraw.Draw(img)
    tc = theme["text"]

    draw.text((50, 36), f"Прогноз  {city}", font=font_bold(46), fill=tc)
    draw.text((52, 94), "На 7 дней", font=font_reg(24), fill=(*tc[:3],180))

    n = len(days[:7])
    total_gap = 12
    card_w = (W - 50*2 - total_gap*(n-1)) // n
    card_h = 390
    sy = 138

    for i, day in enumerate(days[:7]):
        x = 50 + i*(card_w+total_gap)
        img = glass_rect(img, x, sy, x+card_w, sy+card_h, radius=22,
                         fill_color=(255,255,255,38))
        draw = ImageDraw.Draw(img)

        # День
        draw.text((x+card_w//2, sy+14), day["day"],
                  font=font_bold(19), fill=tc, anchor="mt")
        # Дата
        draw.text((x+card_w//2, sy+40), day["date"],
                  font=font_reg(15), fill=(*tc[:3],175), anchor="mt")

        # Иконка
        draw_icon(img, x+card_w//2, sy+108, day["icon"], size=46)
        draw = ImageDraw.Draw(img)

        # Макс
        draw.text((x+card_w//2, sy+158), f"{day['max']}°",
                  font=font_bold(36), fill=tc, anchor="mt")
        # Мин
        draw.text((x+card_w//2, sy+200), f"{day['min']}°",
                  font=font_reg(24), fill=(*tc[:3],155), anchor="mt")

        # Разделитель
        draw.line([(x+12, sy+240), (x+card_w-12, sy+240)],
                  fill=(*tc[:3],40), width=1)

        # Детали
        draw.text((x+card_w//2, sy+254), f"Влажн. {day['humidity']}%",
                  font=font_reg(15), fill=(*tc[:3],195), anchor="mt")
        draw.text((x+card_w//2, sy+278), f"Ветер {day['wind']} м/с",
                  font=font_reg(15), fill=(*tc[:3],195), anchor="mt")

        # Описание
        desc = day["desc"][:11]
        draw.text((x+card_w//2, sy+316), desc,
                  font=font_reg(13), fill=(*tc[:3],155), anchor="mt")

    buf = BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=95)
    buf.seek(0)
    return buf
