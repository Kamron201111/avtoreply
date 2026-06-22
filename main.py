"""Loyiha ildizidan ishga tushirish uchun yorliq."""
from app.main import main
import asyncio

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot to'xtatildi")
