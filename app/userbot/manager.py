"""
Userbot menejeri — saqlangan session_string orqali:
  • foydalanuvchi guruhlarini olish
  • guruhlarga avto-xabar yuborish
  • autoreply (DM avtomatik javob) ulash
"""
import asyncio
from typing import Optional

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import Channel, Chat
from telethon.errors import (
    ChatWriteForbiddenError,
    UserBannedInChannelError,
    FloodWaitError,
    ChannelPrivateError,
    SlowModeWaitError,
)

from app.config import config
from app.database import db


# account_id → ulangan TelegramClient (avto-yuborish va autoreply uchun)
_clients: dict[int, TelegramClient] = {}


async def get_client(account_id: int, session_string: str) -> Optional[TelegramClient]:
    """Akkaunt uchun ulangan klient qaytaradi (cache bilan)."""
    if account_id in _clients and _clients[account_id].is_connected():
        return _clients[account_id]

    client = TelegramClient(
        StringSession(session_string),
        config.api_id,
        config.api_hash,
        device_model="Auto Habar Pro",
    )
    try:
        await client.connect()
        if not await client.is_user_authorized():
            await client.disconnect()
            return None
        _clients[account_id] = client
        return client
    except Exception:
        return None


async def disconnect_client(account_id: int) -> None:
    client = _clients.pop(account_id, None)
    if client:
        try:
            await client.disconnect()
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════
# GURUHLARNI OLISH
# ═══════════════════════════════════════════════════════════════════

async def fetch_user_groups(session_string: str) -> list[dict]:
    """
    Akkaunt a'zo bo'lgan barcha guruh/superguruhlarni qaytaradi.
    """
    client = TelegramClient(
        StringSession(session_string), config.api_id, config.api_hash,
    )
    groups: list[dict] = []
    try:
        await client.connect()
        if not await client.is_user_authorized():
            return []

        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            # Faqat guruh va superguruhlar (kanal emas)
            is_group = False
            if isinstance(entity, Chat):
                is_group = True
            elif isinstance(entity, Channel) and entity.megagroup:
                is_group = True

            if is_group:
                groups.append({
                    "chat_id": dialog.id,
                    "title": dialog.title or "Guruh",
                })
    except Exception as e:
        print(f"[fetch_user_groups] xato: {e}")
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass
    return groups


# ═══════════════════════════════════════════════════════════════════
# AVTO-XABAR YUBORISH
# ═══════════════════════════════════════════════════════════════════

async def send_to_group(
    client: TelegramClient,
    chat_id: int,
    text: str,
    file_id: str = "",
) -> dict:
    """
    Bitta guruhga xabar yuboradi.
    Returns: {"ok": True} yoki {"ok": False, "error": "...", "flood": sec}
    """
    try:
        # Eslatma: Bot file_id'lari userbot'da ishlamaydi.
        # Shuning uchun userbot uchun matn yuboriladi (rasm URL/yo'l bilan kengaytirsa bo'ladi).
        await client.send_message(chat_id, text, parse_mode="html")
        return {"ok": True}
    except FloodWaitError as e:
        return {"ok": False, "error": "FLOOD_WAIT", "flood": e.seconds}
    except SlowModeWaitError as e:
        return {"ok": False, "error": "SLOW_MODE", "flood": e.seconds}
    except ChatWriteForbiddenError:
        return {"ok": False, "error": "Yozish taqiqlangan"}
    except UserBannedInChannelError:
        return {"ok": False, "error": "Guruhda banlangansiz"}
    except ChannelPrivateError:
        return {"ok": False, "error": "Guruh yopiq yoki chiqarilgan"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:150]}


async def broadcast_account(account: dict) -> dict:
    """
    Bitta akkauntning barcha yoqilgan guruhlariga xabar yuboradi.
    Statistikani DB ga yozadi.
    """
    account_id = account["id"]
    session = account["session_string"]
    text = account.get("message_text", "")

    if not text:
        return {"sent": 0, "failed": 0, "error": "Xabar matni yo'q"}

    client = await get_client(account_id, session)
    if not client:
        return {"sent": 0, "failed": 0, "error": "Akkaunt ulanmadi (session eskirgan?)"}

    groups = await db.get_enabled_groups(account_id)
    sent = failed = 0

    for g in groups:
        res = await send_to_group(client, g["chat_id"], text, account.get("message_file_id", ""))
        if res["ok"]:
            sent += 1
            await db.log_send(account_id, g["chat_id"], "sent")
        else:
            failed += 1
            await db.log_send(account_id, g["chat_id"], "failed", res.get("error", ""))
            # Flood bo'lsa biroz kutamiz
            if res.get("flood"):
                await asyncio.sleep(min(res["flood"], 30))
        # Guruhlar orasida kichik pauza (flood oldini olish)
        await asyncio.sleep(2)

    return {"sent": sent, "failed": failed}


# ═══════════════════════════════════════════════════════════════════
# AUTOREPLY (DM avtomatik javob)
# ═══════════════════════════════════════════════════════════════════

_autoreply_handlers: dict[int, object] = {}


async def enable_autoreply(account_id: int, session_string: str, reply_text: str) -> bool:
    """Akkaunt uchun DM autoreply'ni yoqadi."""
    client = await get_client(account_id, session_string)
    if not client:
        return False

    # Avvalgi handlerni o'chiramiz
    await disable_autoreply(account_id)

    async def handler(event):
        # Faqat shaxsiy xabarlar (DM), o'zimiznikidan emas
        if event.is_private and not event.out:
            try:
                await event.reply(reply_text, parse_mode="html")
            except Exception:
                pass

    client.add_event_handler(handler, events.NewMessage(incoming=True))
    _autoreply_handlers[account_id] = handler
    return True


async def disable_autoreply(account_id: int) -> None:
    handler = _autoreply_handlers.pop(account_id, None)
    client = _clients.get(account_id)
    if handler and client:
        try:
            client.remove_event_handler(handler)
        except Exception:
            pass
