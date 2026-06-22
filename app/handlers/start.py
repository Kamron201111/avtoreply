"""
Start + til tanlash + asosiy menyu (3 tilli, raw API).
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards import reply
from app.raw_api import send_message, edit_message, answer_callback, delete_message
from app.i18n import t
from app.lang_util import get_lang, set_cache
from app.config import config

router = Router(name="start")


async def show_main_menu(user_id: int, lang: str = None) -> None:
    """Asosiy menyuni ko'rsatadi."""
    if lang is None:
        lang = await get_lang(user_id)
    name = ""
    user = await db.get_user(user_id)
    if user:
        name = user["full_name"] or user["username"] or "Foydalanuvchi"
    is_admin = config.is_admin(user_id)
    await send_message(user_id, t("welcome", lang, name=name),
                       reply_markup=reply.main_menu(lang, is_admin))


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await db.get_or_create_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name or "",
    )
    if user["is_banned"]:
        await message.answer("🚫 Bloklangansiz.")
        return

    # Til tanlanmaganmi? — til tanlashni ko'rsatamiz
    if not user["lang"]:
        await send_message(message.from_user.id, t("choose_lang", "uz"),
                           reply_markup=reply.lang_kb())
        return

    set_cache(message.from_user.id, user["lang"])
    await show_main_menu(message.from_user.id, user["lang"])


# ─── Til tanlash ────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("setlang_"))
async def cb_setlang(call: CallbackQuery, state: FSMContext):
    lang = call.data.split("_")[1]
    if lang not in ("uz", "ru", "en"):
        lang = "uz"
    await db.set_lang(call.from_user.id, lang)
    set_cache(call.from_user.id, lang)
    try:
        await delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    await send_message(call.from_user.id, t("lang_set", lang))
    await show_main_menu(call.from_user.id, lang)
    await answer_callback(call.id)


@router.message(Command("lang"))
async def cmd_lang(message: Message, state: FSMContext):
    await state.clear()
    await send_message(message.from_user.id, t("choose_lang", "uz"),
                       reply_markup=reply.lang_kb())


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    await state.clear()
    user = await db.get_or_create_user(
        message.from_user.id, message.from_user.username or "",
        message.from_user.full_name or "")
    if not user["lang"]:
        await send_message(message.from_user.id, t("choose_lang", "uz"),
                           reply_markup=reply.lang_kb())
        return
    await show_main_menu(message.from_user.id, user["lang"])
