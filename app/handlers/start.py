"""
Start va asosiy menyu handlerlari.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards import menus
from app import emoji as em
from app.config import config

router = Router(name="main")


def welcome_text(user) -> str:
    uname = f"@{user['username']}" if user["username"] else user["full_name"]
    prem = em.eST() + " <b>Premium</b>" if user["is_premium"] else "Oddiy"
    return (
        f"{em.eW()} Assalomu alaykum, <b>{uname}</b>!\n\n"
        f"{em.eRK()} <b>AUTO HABAR PRO</b> — guruhlarga avtomatik xabar yuborish boti.\n\n"
        f"{em.eID()} ID: <code>{user['telegram_id']}</code>\n"
        f"💼 Tarif: {prem}\n\n"
        f"Quyidagi menyudan kerakli bo'limni tanlang:"
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
    await message.answer(welcome_text(user), reply_markup=menus.main_menu())


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    await state.clear()
    if not config.is_admin(message.from_user.id):
        await message.answer("❌ Sizda admin huquqi yo'q.")
        return
    await message.answer("🛠 <b>Admin panel</b>", reply_markup=menus.admin_menu())


@router.callback_query(F.data == "back_main")
async def cb_back_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    user = await db.get_user(call.from_user.id)
    await call.message.edit_text(welcome_text(user), reply_markup=menus.main_menu())
    await call.answer()


@router.callback_query(F.data == "help")
async def cb_help(call: CallbackQuery):
    text = (
        f"{em.eIN()} <b>Yordam</b>\n\n"
        f"{em.eRK()} <b>Bot nima qiladi?</b>\n"
        f"Sizning akkauntingiz nomidan tanlangan guruhlarga "
        f"belgilangan vaqt oralig'ida avtomatik xabar yuboradi.\n\n"
        f"📌 <b>Qanday ishlatish:</b>\n"
        f"1. <b>Akkaunt qo'shing</b> (QR yoki SMS orqali)\n"
        f"2. <b>Guruhlarni</b> tanlang\n"
        f"3. <b>Habar matni</b>ni yozing\n"
        f"4. <b>Interval</b>ni belgilang\n"
        f"5. <b>Ishga tushuring</b> ✅\n\n"
        f"{em.eCL()} <b>Autoreply</b> — siz onlayn bo'lmaganda DM'ga avto-javob beradi.\n\n"
        f"❓ Savol bo'lsa: @{config.admin_username}"
    )
    await call.message.edit_text(text, reply_markup=menus.back_main())
    await call.answer()


@router.callback_query(F.data == "stats")
async def cb_stats(call: CallbackQuery):
    accounts = await db.get_accounts(call.from_user.id)
    if not accounts:
        await call.answer("Avval akkaunt qo'shing!", show_alert=True)
        return

    text = f"{em.eST()} <b>Statistika</b>\n\n"
    for a in accounts:
        st = await db.get_stats(a["id"])
        gc = await db.count_groups(a["id"])
        name = a["account_name"] or a["phone"] or f"#{a['id']}"
        status = "🟢 Ishlamoqda" if a["is_active"] else "🔴 To'xtagan"
        text += (
            f"👤 <b>{name}</b> — {status}\n"
            f"   {em.eGR()} Guruhlar: <b>{gc}</b>\n"
            f"   ✅ Yuborilgan: <b>{st['sent']}</b>\n"
            f"   📅 Bugun: <b>{st['today']}</b>\n"
            f"   ❌ Xato: <b>{st['failed']}</b>\n\n"
        )
    await call.message.edit_text(text, reply_markup=menus.back_main())
    await call.answer()


@router.callback_query(F.data == "settings")
async def cb_settings(call: CallbackQuery):
    text = (
        f"{em.eGE()} <b>Sozlamalar</b>\n\n"
        f"Bu yerdagi sozlamalar botning umumiy ishlash tartibiga ta'sir qiladi.\n\n"
        f"Akkaunt sozlamalari uchun <b>Akkauntlar</b> bo'limiga o'ting."
    )
    await call.message.edit_text(text, reply_markup=menus.back_main())
    await call.answer()
