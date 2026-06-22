"""
Foydalanuvchi tilini olish yordamchisi.
Tilni xotirada keshlaymiz (har safar DB so'rovini kamaytirish uchun).
"""
from app.database import db

_cache: dict[int, str] = {}


async def get_lang(user_id: int) -> str:
    """Foydalanuvchi tilini qaytaradi (keshdan yoki DB dan)."""
    if user_id in _cache:
        return _cache[user_id]
    user = await db.get_user(user_id)
    lang = (user["lang"] if user and user["lang"] else "uz")
    _cache[user_id] = lang
    return lang


def set_cache(user_id: int, lang: str) -> None:
    _cache[user_id] = lang


def clear_cache(user_id: int) -> None:
    _cache.pop(user_id, None)
