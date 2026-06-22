"""
FSM holatlari — ulash, xabar sozlash, autoreply va admin uchun.
"""
from aiogram.fsm.state import State, StatesGroup


class LinkAccount(StatesGroup):
    """Akkaunt ulash jarayoni."""
    choosing_method = State()    # QR yoki SMS tanlash
    waiting_phone = State()      # SMS: telefon raqami
    waiting_code = State()       # SMS: kod
    waiting_password = State()   # 2FA parol (QR/SMS umumiy)
    qr_waiting = State()         # QR skaner kutilmoqda


class MessageSetup(StatesGroup):
    """Avto-xabar matnini sozlash."""
    waiting_text = State()
    waiting_interval = State()


class AutoReplySetup(StatesGroup):
    """Autoreply matnini sozlash."""
    waiting_text = State()


class AdminStates(StatesGroup):
    """Admin panel holatlari."""
    waiting_broadcast = State()
    waiting_user_id = State()
    waiting_premium_id = State()
    waiting_prices = State()
    waiting_card = State()


class ProGift(StatesGroup):
    """Pro sovg'a qilish holatlari."""
    waiting_target = State()     # kimga sovg'a (username/ID)
    waiting_payment = State()    # to'lov tasdiqlash
