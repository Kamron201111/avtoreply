"""
AUTO HABAR PRO — asosiy ishga tushirish fayli.

Ishga tushirish:
    python -m app.main
yoki
    python main.py
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import config
from app.database import db
from app.services import scheduler
from app.handlers import start, accounts, manage, admin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("autohabar")


async def main():
    if not config.bot_token:
        raise RuntimeError("BOT_TOKEN .env da o'rnatilmagan!")
    if not config.api_id or not config.api_hash:
        raise RuntimeError("TG_API_ID / TG_API_HASH .env da o'rnatilmagan!")

    # Ma'lumotlar bazasi
    log.info("PostgreSQL ulanmoqda...")
    await db.init_pool()
    log.info("✅ DB tayyor")

    # Bot
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Routerlar (tartib muhim — aniqroq filtrlar avval)
    dp.include_router(start.router)
    dp.include_router(accounts.router)
    dp.include_router(manage.router)
    dp.include_router(admin.router)

    # Avto-yuborish scheduler va autoreply tiklash
    asyncio.create_task(scheduler.scheduler_loop())
    await scheduler.restore_autoreplies()

    log.info("🚀 Bot ishga tushdi!")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await db.close_pool()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Bot to'xtatildi")
