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
    auto_delete_sec: int = 0,
) -> dict:
    """
    Bitta guruhga xabar yuboradi.
    auto_delete_sec > 0 bo'lsa — xabar shu vaqtdan keyin o'chiriladi.
    Returns: {"ok": True} yoki {"ok": False, "error": "...", "flood": sec}
    """
    try:
        msg = await client.send_message(chat_id, text, parse_mode="html")
        # Avto-o'chirish (fon vazifa)
        if auto_delete_sec and auto_delete_sec > 0 and msg:
            async def _del():
                await asyncio.sleep(auto_delete_sec)
                try:
                    await client.delete_messages(chat_id, [msg.id])
                except Exception:
                    pass
            asyncio.create_task(_del())
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
    Mention yoqilgan bo'lsa — guruh a'zosini @mention qiladi.
    Statistikani DB ga yozadi.
    """
    account_id = account["id"]
    session = account["session_string"]
    text = account.get("message_text", "")
    mention_on = account.get("mention_enabled", False)
    auto_del = account.get("auto_delete_sec", 0)

    if not text:
        return {"sent": 0, "failed": 0, "error": "Xabar matni yo'q"}

    client = await get_client(account_id, session)
    if not client:
        return {"sent": 0, "failed": 0, "error": "Akkaunt ulanmadi (session eskirgan?)"}

    groups = await db.get_enabled_groups(account_id)
    sent = failed = 0

    for g in groups:
        send_text = text
        # Mention — guruhdan tasodifiy a'zoni @mention qilish
        if mention_on:
            try:
                mention_str = await _get_random_mention(client, g["chat_id"])
                if mention_str:
                    send_text = f"{mention_str} {text}"
            except Exception:
                pass

        res = await send_to_group(client, g["chat_id"], send_text,
                                  account.get("message_file_id", ""), auto_del)
        if res["ok"]:
            sent += 1
            await db.log_send(account_id, g["chat_id"], "sent")
        else:
            failed += 1
            await db.log_send(account_id, g["chat_id"], "failed", res.get("error", ""))
            if res.get("flood"):
                await asyncio.sleep(min(res["flood"], 30))
        await asyncio.sleep(2)

    # Tsiklni hisoblaymiz
    await db.inc_cycle(account_id)
    return {"sent": sent, "failed": failed}


async def _get_random_mention(client, chat_id) -> str:
    """Guruhdan tasodifiy a'zoni @mention qiladi (link ko'rinishida)."""
    import random
    members = []
    try:
        async for user in client.iter_participants(chat_id, limit=50):
            if not user.bot and not user.deleted:
                members.append(user)
    except Exception:
        return ""
    if not members:
        return ""
    u = random.choice(members)
    if u.username:
        return f"@{u.username}"
    # username yo'q bo'lsa — inline mention (HTML)
    name = u.first_name or "user"
    return f'<a href="tg://user?id={u.id}">{name}</a>'


# ═══════════════════════════════════════════════════════════════════
# DM JAVOB (onlayn bo'lmaganda shaxsiy xabarga javob) — Image 9
# ═══════════════════════════════════════════════════════════════════
import time

_dm_handlers: dict[int, object] = {}
_dm_last_reply: dict[tuple, float] = {}   # (account_id, peer_id) -> vaqt


async def enable_dm_reply(account_id: int, session_string: str, reply_text: str) -> bool:
    """DM javob — siz offline bo'lganda shaxsiy xabarlarga javob."""
    client = await get_client(account_id, session_string)
    if not client:
        return False
    await disable_dm_reply(account_id)

    async def handler(event):
        # Faqat kiruvchi shaxsiy xabar, o'zimizdan emas
        if not event.is_private or event.out:
            return
        sender = await event.get_sender()
        # Bot bo'lsa javob bermaymiz
        if getattr(sender, "bot", False):
            return
        # Har bir chatga 10 soniyada 1 marta
        key = (account_id, event.chat_id)
        now = time.time()
        if now - _dm_last_reply.get(key, 0) < 10:
            return
        _dm_last_reply[key] = now
        try:
            await event.reply(reply_text, parse_mode="html")
        except Exception:
            pass

    client.add_event_handler(handler, events.NewMessage(incoming=True))
    _dm_handlers[account_id] = handler
    return True


async def disable_dm_reply(account_id: int) -> None:
    handler = _dm_handlers.pop(account_id, None)
    client = _clients.get(account_id)
    if handler and client:
        try:
            client.remove_event_handler(handler)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════
# AUTOREPLY (guruhda kimdir sizni reply qilsa javob) — Image 12
# ═══════════════════════════════════════════════════════════════════
_group_handlers: dict[int, object] = {}
_group_last: dict[tuple, float] = {}


async def enable_group_reply(account_id: int, session_string: str,
                             reply_text: str, usernames: list) -> bool:
    """Guruhda sizning xabaringizga reply qilinsa avtomatik javob."""
    client = await get_client(account_id, session_string)
    if not client:
        return False
    await disable_group_reply(account_id)

    # username larni kichik harfga (solishtirish uchun)
    allow = set(u.lower().lstrip("@") for u in usernames) if usernames else set()
    me = await client.get_me()
    my_id = me.id

    async def handler(event):
        # Faqat guruh xabari, reply bo'lishi kerak
        if event.is_private or event.out or not event.is_reply:
            return
        # Guruh username filtri (agar ro'yxat bo'lsa)
        if allow:
            chat = await event.get_chat()
            cu = (getattr(chat, "username", "") or "").lower()
            if cu not in allow:
                return
        # Reply mening xabarimgami?
        replied = await event.get_reply_message()
        if not replied or replied.sender_id != my_id:
            return
        # 10 soniya throttle
        key = (account_id, event.chat_id)
        now = time.time()
        if now - _group_last.get(key, 0) < 10:
            return
        _group_last[key] = now
        try:
            await event.reply(reply_text, parse_mode="html")
        except Exception:
            pass

    client.add_event_handler(handler, events.NewMessage(incoming=True))
    _group_handlers[account_id] = handler
    return True


async def disable_group_reply(account_id: int) -> None:
    handler = _group_handlers.pop(account_id, None)
    client = _clients.get(account_id)
    if handler and client:
        try:
            client.remove_event_handler(handler)
        except Exception:
            pass
