"""
AUTO HABAR PRO — asosiy ishga tushirish.
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import config
from app.database import db
from app.services import scheduler
from app import raw_api
from app.handlers import start, menu, accounts, manage, admin, pro

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("autohabar")


async def main():
    if not config.bot_token:
        raise RuntimeError("BOT_TOKEN yo'q!")
    if not config.api_id or not config.api_hash:
        raise RuntimeError("TG_API_ID / TG_API_HASH yo'q!")

    log.info("PostgreSQL ulanmoqda...")
    await db.init_pool()
    log.info("✅ DB tayyor")

    bot = Bot(token=config.bot_token,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Routerlar (tartib muhim!)
    # start — buyruqlar + til tanlash
    # accounts + manage — FSM state handlerlari (MENU dan oldin)
    # pro — Pro to'lov + murojat state
    # menu — reply tugmalari
    # admin — admin panel (state + reply tugma)
    dp.include_router(start.router)
    dp.include_router(accounts.router)
    dp.include_router(manage.router)
    dp.include_router(pro.router)
    dp.include_router(admin.router)
    dp.include_router(menu.router)

    # Scheduler + reply'larni tiklash
    asyncio.create_task(scheduler.scheduler_loop())
    await scheduler.restore_replies()

    log.info("🚀 Bot ishga tushdi!")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await raw_api.close_session()
        await db.close_pool()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("To'xtatildi")
