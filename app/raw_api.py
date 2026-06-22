"""
Raw Telegram API yordamchisi.

Inline tugmalarda style (rang) va icon_custom_emoji_id (premium emoji)
ishlashi uchun xabarlarni to'g'ridan-to'g'ri Telegram API'ga yuboramiz.
Bitta aiohttp sessiyasi orqali — tez va resurs-tejamkor.
"""
import logging
from typing import Any, Optional

import aiohttp

from app.config import config

log = logging.getLogger(__name__)
_API = f"https://api.telegram.org/bot{config.bot_token}"

_session: Optional[aiohttp.ClientSession] = None


async def _get_session() -> aiohttp.ClientSession:
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession()
    return _session


async def close_session() -> None:
    global _session
    if _session and not _session.closed:
        await _session.close()


async def call(method: str, **params: Any) -> Optional[dict]:
    """Telegram API metodini chaqiradi. 'result' qaytadi yoki None."""
    payload = {k: v for k, v in params.items() if v is not None}
    session = await _get_session()
    try:
        async with session.post(f"{_API}/{method}", json=payload, timeout=60) as resp:
            data = await resp.json()
            if not data.get("ok"):
                log.warning("API %s xato: %s", method, data.get("description"))
                return None
            return data.get("result")
    except Exception as e:
        log.error("API %s ulanish xatosi: %s", method, e)
        return None


async def send_message(chat_id: int, text: str, *,
                       reply_markup: Optional[dict] = None,
                       parse_mode: str = "HTML",
                       disable_preview: bool = True) -> Optional[dict]:
    """Premium emoji + rangli tugmalar bilan xabar yuborish."""
    return await call(
        "sendMessage",
        chat_id=chat_id,
        text=text,
        parse_mode=parse_mode,
        link_preview_options={"is_disabled": disable_preview},
        reply_markup=reply_markup,
    )


async def edit_message(chat_id: int, message_id: int, text: str, *,
                       reply_markup: Optional[dict] = None,
                       parse_mode: str = "HTML") -> Optional[dict]:
    return await call(
        "editMessageText",
        chat_id=chat_id,
        message_id=message_id,
        text=text,
        parse_mode=parse_mode,
        link_preview_options={"is_disabled": True},
        reply_markup=reply_markup,
    )


async def answer_callback(callback_id: str, text: str = "",
                          show_alert: bool = False) -> None:
    await call("answerCallbackQuery", callback_query_id=callback_id,
               text=text, show_alert=show_alert)


async def delete_message(chat_id: int, message_id: int) -> None:
    await call("deleteMessage", chat_id=chat_id, message_id=message_id)


# ─── dict keyboard -> aiogram InlineKeyboardMarkup (accounts.py uchun) ──
def to_aiogram_markup(kb_dict: dict):
    """
    Raw dict keyboardni aiogram InlineKeyboardMarkup'ga aylantiradi.
    style/icon aiogram'da ham qo'llab-quvvatlanadi (3.29+).
    """
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    if not kb_dict or "inline_keyboard" not in kb_dict:
        return None
    rows = []
    for row in kb_dict["inline_keyboard"]:
        new_row = []
        for b in row:
            kwargs = {"text": b["text"]}
            if "callback_data" in b:
                kwargs["callback_data"] = b["callback_data"]
            if "url" in b:
                kwargs["url"] = b["url"]
            if "icon_custom_emoji_id" in b:
                kwargs["icon_custom_emoji_id"] = b["icon_custom_emoji_id"]
            if "style" in b:
                kwargs["style"] = b["style"]
            new_row.append(InlineKeyboardButton(**kwargs))
        rows.append(new_row)
    return InlineKeyboardMarkup(inline_keyboard=rows)
