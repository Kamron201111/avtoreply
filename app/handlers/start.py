"""
Start va asosiy menyu handlerlari (ReplyKeyboard — pastdagi tugmalar).
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards import reply
from app import emoji as em
from app.config import config

router = Router(name="main")


def welcome_text(user) -> str:
    """Skrinshотdagi salomlashish xabari (premium emoji bilan)."""
    name = user["full_name"] or user["username"] or "Foydalanuvchi"
    return (
        f"{em.pe('rocket')} <b>AUTO HABAR PRO</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Salom, <b>{name}</b> {em.pe('wave')}\n\n"
        f"<blockquote>"
        f"› Akkaunt qo'shing\n"
        f"› Guruhlarni sozlang\n"
        f"› Habarni sozlang\n"
        f"› Autohabarni ishga tushuring"
        f"</blockquote>"
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
    await message.answer(welcome_text(user), reply_markup=reply.main_menu())


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    await state.clear()
    if not config.is_admin(message.from_user.id):
        await message.answer("❌ Sizda admin huquqi yo'q.")
        return
    from app.keyboards import menus
    await message.answer("🛠 <b>Admin panel</b>", reply_markup=menus.admin_menu())


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    await state.clear()
    user = await db.get_or_create_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name or "",
    )
    await message.answer(welcome_text(user), reply_markup=reply.main_menu())
