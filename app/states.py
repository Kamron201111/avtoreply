"""
FSM holatlari.
"""
from aiogram.fsm.state import State, StatesGroup


class LinkAccount(StatesGroup):
    choosing_method = State()
    waiting_phone = State()
    waiting_code = State()
    waiting_password = State()
    qr_waiting = State()


class MessageSetup(StatesGroup):
    waiting_text = State()
    waiting_interval = State()


class AutoReplySetup(StatesGroup):
    waiting_text = State()


class DMReplySetup(StatesGroup):
    """DM javob (onlayn bo'lmaganda)."""
    waiting_text = State()


class GroupReplySetup(StatesGroup):
    """Autoreply (guruhda reply qilinsa)."""
    waiting_text = State()
    waiting_groups = State()


class AdminStates(StatesGroup):
    waiting_broadcast = State()
    waiting_user_id = State()
    waiting_premium_id = State()
    waiting_prices = State()
    waiting_card = State()
    waiting_guide = State()
    waiting_statsdesc = State()
    waiting_help = State()
    waiting_channel = State()
    waiting_ticket_reply = State()


class ProGift(StatesGroup):
    waiting_target = State()
    waiting_payment = State()


class Support(StatesGroup):
    """Murojat (foydalanuvchi -> admin)."""
    waiting_message = State()
