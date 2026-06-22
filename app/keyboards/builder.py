"""
Tugma qurilishi — Bot API 9.4 (style + icon_custom_emoji_id) bilan.

Tugmalar dict ko'rinishida quriladi va raw API orqali yuboriladi,
shunda style (rang) va icon (premium emoji) ishlaydi.

style: "primary" (ko'k) | "success" (yashil) | "danger" (qizil) | "" (default)
icon:  emoji.ICON kaliti (masalan "ROCKET") yoki to'g'ridan-to'g'ri ID
"""
from app.emoji import ICON


def btn(text: str, *, cb: str = "", url: str = "", web_app: str = "",
        icon: str = "", style: str = "", switch_inline: str = "") -> dict:
    """Bitta inline tugma (dict)."""
    b: dict = {"text": text}
    if cb:
        b["callback_data"] = cb
    if url:
        b["url"] = url
    if web_app:
        b["web_app"] = {"url": web_app}
    if switch_inline != "":
        b["switch_inline_query_current_chat"] = switch_inline
    if icon:
        b["icon_custom_emoji_id"] = ICON.get(icon, icon)
    if style:
        b["style"] = style
    return b


def inline_kb(rows: list[list[dict]]) -> dict:
    """reply_markup uchun inline keyboard dict."""
    return {"inline_keyboard": rows}


def reply_kb(rows: list[list[dict]], *, resize: bool = True,
             one_time: bool = False, persistent: bool = True,
             placeholder: str = "") -> dict:
    """Pastdan chiqadigan reply keyboard."""
    kb: dict = {"keyboard": rows, "resize_keyboard": resize}
    if one_time:
        kb["one_time_keyboard"] = True
    if persistent:
        kb["is_persistent"] = True
    if placeholder:
        kb["input_field_placeholder"] = placeholder
    return kb


def rbtn(text: str, *, icon: str = "", style: str = "") -> dict:
    """Reply keyboard tugmasi (matn yuboradi)."""
    b: dict = {"text": text}
    if icon:
        b["icon_custom_emoji_id"] = ICON.get(icon, icon)
    if style:
        b["style"] = style
    return b


# ─── Eski aiogram-uslub funksiyalar bilan moslik (manage.py uchun) ──
def kb(rows):
    """Eski kod uchun — dict inline_kb qaytaradi."""
    # Agar InlineKeyboardButton obyektlari kelsa ularni dict'ga aylantiramiz
    new_rows = []
    for row in rows:
        new_row = []
        for b in row:
            if isinstance(b, dict):
                new_row.append(b)
            else:
                # aiogram InlineKeyboardButton -> dict
                d = {"text": b.text}
                if b.callback_data:
                    d["callback_data"] = b.callback_data
                if getattr(b, "url", None):
                    d["url"] = b.url
                if getattr(b, "style", None):
                    d["style"] = b.style
                new_row.append(d)
        new_rows.append(new_row)
    return inline_kb(new_rows)
