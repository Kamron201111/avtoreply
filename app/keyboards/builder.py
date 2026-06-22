"""
Rangli inline tugmalar (aiogram 3.x).

emoji  — emoji nomi (em.E_*) yoki oddiy emoji; tugma matni OLDIGA qo'shiladi
style  — tugma rangi (Bot API 9.4): "primary", "success", "danger"

ESLATMA: Inline tugmalarda premium emoji (icon_custom_emoji_id) ishlatilmaydi,
chunki u DOCUMENT_INVALID berishi mumkin. Oddiy emoji matn oldiga qo'shiladi.
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app import emoji as em


def _resolve_emoji(emoji: str) -> str:
    """Emoji nomini (masalan 'rocket') oddiy emojiga aylantiradi."""
    if not emoji:
        return ""
    # Agar bu nom bo'lsa (PLAIN ichida) — oddiy emoji qaytar
    if emoji in em.PLAIN:
        return em.PLAIN[emoji]
    # Aks holda o'zi emoji (masalan to'g'ridan-to'g'ri "🚀")
    return emoji


def btn(
    text: str,
    callback_data: str = "",
    url: str = "",
    emoji: str = "",
    style: str = "",
) -> InlineKeyboardButton:
    """Bitta inline tugma yaratadi."""
    icon = _resolve_emoji(emoji)
    label = f"{icon} {text}".strip() if icon else text

    kwargs: dict = {"text": label}
    if callback_data:
        kwargs["callback_data"] = callback_data
    if url:
        kwargs["url"] = url
    if style:
        kwargs["style"] = style   # Bot API 9.4 — rang (xavfsiz)
    return InlineKeyboardButton(**kwargs)


def kb(rows: list[list[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
    """Tugma qatorlaridan klaviatura yasaydi."""
    return InlineKeyboardMarkup(inline_keyboard=rows)
