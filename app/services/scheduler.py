"""
Avto-yuborish scheduler — fon vazifa.

Har 30 soniyada barcha faol akkauntlarni tekshiradi:
agar akkauntning next_send_at vaqti yetgan bo'lsa — guruhlarga xabar yuboradi
va keyingi yuborish vaqtini belgilaydi.
"""
import asyncio
from datetime import datetime, timedelta, timezone

from app.database import db
from app.userbot import manager


# Ayni paytda yuborilayotgan akkauntlar (takror oldini olish)
_busy: set[int] = set()


async def scheduler_loop():
    """Asosiy scheduler tsikli."""
    print("[scheduler] ishga tushdi")
    while True:
        try:
            await _tick()
        except Exception as e:
            print(f"[scheduler] xato: {e}")
        await asyncio.sleep(30)


async def _tick():
    """Bitta tekshiruv tsikli."""
    accounts = await db.get_active_accounts()
    now = datetime.now(timezone.utc)

    for account in accounts:
        account_id = account["id"]

        # Allaqachon yuborilayotgan bo'lsa — o'tkazib yuboramiz
        if account_id in _busy:
            continue

        next_send = account["next_send_at"]
        if next_send is None:
            # Birinchi marta — darhol yuborish vaqtini belgilaymiz
            nxt = now + timedelta(minutes=account["interval_min"])
            await db.set_running(account_id, True, nxt)
            continue

        # Vaqt yetdimi?
        if now >= next_send:
            asyncio.create_task(_send_account(dict(account)))


async def _send_account(account: dict):
    """Bitta akkauntga xabar yuborish + keyingi vaqtni belgilash."""
    account_id = account["id"]
    _busy.add(account_id)
    try:
        result = await manager.broadcast_account(account)
        print(f"[scheduler] account#{account_id}: "
              f"sent={result.get('sent',0)} failed={result.get('failed',0)}")

        # Keyingi yuborish vaqti
        interval = account.get("interval_min", 5)
        next_send = datetime.now(timezone.utc) + timedelta(minutes=interval)

        # Hali ham ishlamoqdami tekshiramiz (foydalanuvchi to'xtatgan bo'lishi mumkin)
        fresh = await db.get_autosend(account_id)
        if fresh and fresh["is_running"]:
            await db.set_running(account_id, True, next_send)
    except Exception as e:
        print(f"[scheduler] _send_account#{account_id} xato: {e}")
    finally:
        _busy.discard(account_id)


async def restore_autoreplies():
    """Bot qayta ishga tushganda yoqilgan autoreply'larni tiklaydi."""
    async with db.pool().acquire() as con:
        rows = await con.fetch("""
            SELECT r.account_id, r.reply_text, a.session_string
            FROM autoreplies r
            JOIN accounts a ON a.id = r.account_id
            WHERE r.is_enabled = TRUE AND a.is_active = TRUE
        """)
    for r in rows:
        try:
            await manager.enable_autoreply(
                r["account_id"], r["session_string"], r["reply_text"]
            )
            print(f"[scheduler] autoreply tiklandi: account#{r['account_id']}")
        except Exception as e:
            print(f"[scheduler] autoreply tiklanmadi #{r['account_id']}: {e}")
