"""
Pastdagi tugmalar (ReplyKeyboard) — skrinshотdagi asosiy menyu.

Inline emas, oddiy klaviatura tugmalari (pastda chiqadi).
Tugma matnida ODDIY emoji (ReplyKeyboard premium emoji qo'llab-quvvatlamaydi).
Ranglar Telegram tomonidan avtomatik (mijoz versiyasiga qarab).
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app import emoji as em


# ─── Tugma matnlari (boshqa joyda solishtirish uchun konstanta) ─────
BTN_AUTOSEND = f"{em.oe('rocket')} Autohabar yuborish"
BTN_MESSAGE  = f"{em.oe('edit')} Habar matni"
BTN_INTERVAL = f"{em.oe('clock')} Interval"
BTN_GROUPS   = f"{em.oe('chat')} Guruhlarni sozlash"
BTN_PROFILES = f"{em.oe('profile')} Profillar"
BTN_PRO      = f"{em.oe('crown')} Pro tarif"
BTN_CABINET  = f"{em.oe('user')} Kabinet"
BTN_SETTINGS = f"{em.oe('settings')} Sozlamalar"
BTN_CALENDAR = f"{em.oe('calendar')} Kalendar"
BTN_TOOLS    = f"{em.oe('tools')} Foydali funksiyalar"
BTN_STATS    = f"{em.oe('stats')} Statistika"
BTN_HELP     = f"{em.oe('help')} Yordam"
BTN_GUIDE    = f"{em.oe('book')} Qo'llanma"
BTN_AUTOREPLY = f"{em.oe('autoreply')} Autoreply"


def main_menu() -> ReplyKeyboardMarkup:
    """Skrinshотdagi asosiy menyu (pastdagi tugmalar)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_AUTOSEND), KeyboardButton(text=BTN_MESSAGE)],
            [KeyboardButton(text=BTN_INTERVAL), KeyboardButton(text=BTN_GROUPS)],
            [KeyboardButton(text=BTN_PROFILES), KeyboardButton(text=BTN_PRO)],
            [KeyboardButton(text=BTN_CABINET), KeyboardButton(text=BTN_SETTINGS)],
            [KeyboardButton(text=BTN_CALENDAR), KeyboardButton(text=BTN_TOOLS)],
            [KeyboardButton(text=BTN_STATS), KeyboardButton(text=BTN_HELP)],
            [KeyboardButton(text=BTN_GUIDE), KeyboardButton(text=BTN_AUTOREPLY)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def remove() -> ReplyKeyboardMarkup:
    """Klaviaturani olib tashlash uchun."""
    from aiogram.types import ReplyKeyboardRemove
    return ReplyKeyboardRemove()
