"""
Start va asosiy menyu (raw API — premium emoji + rangli reply keyboard).
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards import reply
from app.raw_api import send_message
from app import emoji as em
from app.config import config

router = Router(name="main")


def welcome_text(user) -> str:
    """Salomlashish xabari (premium emoji bilan)."""
    name = user["full_name"] or user["username"] or "Foydalanuvchi"
    return (
        f"{em.emoji('ROCKET')} <b>AUTO HABAR PRO</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Salom, <b>{name}</b> {em.emoji('WAVE')}\n\n"
        f"<blockquote>"
        f"› Akkaunt qo'shing\n"
        f"› Guruhlarni sozlang\n"
        f"› Habarni sozlang\n"
        f"› Autohabarni ishga tushuring"
        f"</blockquote>"
    )


async def show_main_menu(user_id: int, user) -> None:
    """Asosiy menyuni raw API orqali yuboradi (style ishlashi uchun)."""
    await send_message(
        user_id,
        welcome_text(user),
        reply_markup=reply.main_menu(),
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await db.get_or_create_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name or "",
    )
    if user["is_banned"]:
        await message.answer("🚫 Siz bloklangansiz. Admin bilan bog'laning.")
        return
    await show_main_menu(message.from_user.id, user)


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    await state.clear()
    if not config.is_admin(message.from_user.id):
        await message.answer("❌ Sizda admin huquqi yo'q.")
        return
    from app.keyboards import menus
    from app.raw_api import send_message as sm
    await sm(message.from_user.id, f"{em.emoji('GEAR')} <b>Admin panel</b>",
             reply_markup=menus.admin_menu())


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    await state.clear()
    user = await db.get_or_create_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name or "",
    )
    await show_main_menu(message.from_user.id, user)
