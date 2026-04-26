import asyncio
import logging
from datetime import datetime
from aiogram import Bot
from database.db import get_all_subscribers
from handlers.weather import send_today

logger = logging.getLogger(__name__)


async def scheduler(bot: Bot):
    while True:
        now = datetime.now().strftime("%H:%M")
        subscribers = await get_all_subscribers()
        for user in subscribers:
            if user["notify_time"] == now:
                try:
                    await send_today(bot, user["user_id"], user)
                    logger.info(f"Sent notification to {user['user_id']}")
                except Exception as e:
                    logger.error(f"Notification error for {user['user_id']}: {e}")
        await asyncio.sleep(60)
