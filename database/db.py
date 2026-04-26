import aiosqlite
from pathlib import Path

DATA_DIR = Path("/app/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = str(DATA_DIR / "weather.db")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                city        TEXT,
                lat         REAL,
                lon         REAL,
                notify_time TEXT,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            return await cur.fetchone()


async def upsert_user(user_id: int, city: str = None, lat: float = None,
                      lon: float = None, notify_time: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, city, lat, lon, notify_time)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                city = COALESCE(excluded.city, city),
                lat  = COALESCE(excluded.lat,  lat),
                lon  = COALESCE(excluded.lon,  lon),
                notify_time = COALESCE(excluded.notify_time, notify_time)
        """, (user_id, city, lat, lon, notify_time))
        await db.commit()


async def set_notify(user_id: int, notify_time: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET notify_time = ? WHERE user_id = ?",
                         (notify_time, user_id))
        await db.commit()


async def get_all_subscribers():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE notify_time IS NOT NULL AND lat IS NOT NULL"
        ) as cur:
            return await cur.fetchall()
