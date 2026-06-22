"""
Rangli + premium emoji inline tugmalar (aiogram 3.x).

Elder Stars'dagi `btn()` funksiyasining Python ekvivalenti.
aiogram 3.29+ `style` va `icon_custom_emoji_id` ni qo'llab-quvvatlaydi.
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def btn(
    text: str,
    callback_data: str = "",
    url: str = "",
    emoji: str = "",
    style: str = "",
) -> InlineKeyboardButton:
    """
    Bitta inline tugma yaratadi.

    Args:
        text:          tugma matni
        callback_data: bosilganda yuboriladigan ma'lumot
        url:           havola (callback_data o'rniga)
        emoji:         icon_custom_emoji_id — premium emoji ID
        style:         "primary" (ko'k) | "success" (yashil) | "danger" (qizil)
    """
    kwargs: dict = {"text": text}
    if callback_data:
        kwargs["callback_data"] = callback_data
    if url:
        kwargs["url"] = url
    if emoji:
        kwargs["icon_custom_emoji_id"] = emoji   # Bot API 9.4
    if style:
        kwargs["style"] = style                  # Bot API 9.4
    return InlineKeyboardButton(**kwargs)


def kb(rows: list[list[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
    """Tugma qatorlaridan klaviatura yasaydi."""
    return InlineKeyboardMarkup(inline_keyboard=rows)
