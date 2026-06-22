"""
Admin panel handlerlari — statistika, broadcast, premium boshqaruvi.
"""
import asyncio

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards import menus
from app.states import AdminStates
from app import emoji as em
from app.config import config

router = Router(name="admin")


def _is_admin(user_id: int) -> bool:
    return config.is_admin(user_id)


@router.callback_query(F.data == "adm_main")
async def cb_adm_main(call: CallbackQuery, state: FSMContext):
    if not _is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q", show_alert=True)
        return
    await state.clear()
    await call.message.edit_text("🛠 <b>Admin panel</b>", reply_markup=menus.admin_menu())
    await call.answer()


@router.callback_query(F.data == "adm_stats")
async def cb_adm_stats(call: CallbackQuery):
    if not _is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q", show_alert=True)
        return
    st = await db.get_global_stats()
    text = (
        f"{em.eST()} <b>Umumiy statistika</b>\n\n"
        f"{em.eUS()} Foydalanuvchilar: <b>{st['users']}</b>\n"
        f"📲 Ulangan akkauntlar: <b>{st['accounts']}</b>\n"
        f"🟢 Faol (ishlamoqda): <b>{st['active']}</b>\n"
        f"{em.eGR()} Jami guruhlar: <b>{st['groups']}</b>\n"
        f"✅ Yuborilgan xabarlar: <b>{st['sent_total']}</b>\n"
    )
    await call.message.edit_text(text, reply_markup=menus.admin_back())
    await call.answer()


@router.callback_query(F.data == "adm_users")
async def cb_adm_users(call: CallbackQuery):
    if not _is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q", show_alert=True)
        return
    users = await db.all_users()
    text = f"{em.eUS()} Jami <b>{len(users)}</b> foydalanuvchi:\n\n"
    for u in users[:30]:
        mark = "🚫" if u["is_banned"] else ("⭐️" if u["is_premium"] else "✅")
        uname = f"@{u['username']}" if u["username"] else u["full_name"]
        text += f"{mark} <code>{u['telegram_id']}</code> — {uname}\n"
    if len(users) > 30:
        text += f"\n... va yana {len(users) - 30} ta"
    await call.message.edit_text(text, reply_markup=menus.admin_back())
    await call.answer()


# ─── PREMIUM ────────────────────────────────────────────────────────

@router.callback_query(F.data == "adm_give_premium")
async def cb_give_premium(call: CallbackQuery, state: FSMContext):
    if not _is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_premium_id)
    await state.update_data(action="give")
    await call.message.edit_text(
        f"{em.eOK()} <b>Premium berish</b>\n\n"
        f"Foydalanuvchining Telegram ID raqamini yuboring:",
        reply_markup=menus.admin_back(),
    )
    await call.answer()


@router.callback_query(F.data == "adm_take_premium")
async def cb_take_premium(call: CallbackQuery, state: FSMContext):
    if not _is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_premium_id)
    await state.update_data(action="take")
    await call.message.edit_text(
        f"{em.eWN()} <b>Premium olish</b>\n\n"
        f"Foydalanuvchining Telegram ID raqamini yuboring:",
        reply_markup=menus.admin_back(),
    )
    await call.answer()


@router.message(AdminStates.waiting_premium_id)
async def on_premium_id(message: Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        return
    data = await state.get_data()
    action = data.get("action", "give")
    digits = "".join(c for c in message.text if c.isdigit())
    if not digits:
        await message.answer(f"{em.eWN()} ID faqat raqamlardan iborat.")
        return
    tg_id = int(digits)
    user = await db.get_user(tg_id)
    if not user:
        await message.answer(f"{em.eWN()} Bunday foydalanuvchi topilmadi.")
        return

    give = action == "give"
    await db.set_premium(tg_id, give)
    await state.clear()
    await message.answer(
        f"{em.eOK()} <code>{tg_id}</code> uchun premium "
        f"{'berildi ⭐️' if give else 'olib tashlandi'}!",
        reply_markup=menus.admin_menu(),
    )
    # Foydalanuvchini xabardor qilamiz
    try:
        if give:
            await message.bot.send_message(
                tg_id, f"{em.eST()} <b>Tabriklaymiz!</b>\n\nSizga <b>Premium</b> tarif berildi! 🎉"
            )
        else:
            await message.bot.send_message(
                tg_id, f"{em.eWN()} Sizning Premium tarifingiz tugadi."
            )
    except Exception:
        pass


# ─── BROADCAST ──────────────────────────────────────────────────────

@router.callback_query(F.data == "adm_broadcast")
async def cb_broadcast(call: CallbackQuery, state: FSMContext):
    if not _is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_broadcast)
    await call.message.edit_text(
        f"{em.eRK()} <b>Broadcast xabar</b>\n\n"
        f"Barcha foydalanuvchilarga yubormoqchi bo'lgan xabarni yuboring.\n\n"
        f"📎 Matn, rasm, video — hammasi qo'llab-quvvatlanadi.",
        reply_markup=menus.admin_back(),
    )
    await call.answer()


@router.message(AdminStates.waiting_broadcast)
async def on_broadcast(message: Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        return
    await state.clear()
    users = await db.all_users()
    targets = [u for u in users if not u["is_banned"]]

    progress = await message.answer(
        f"{em.eRK()} <b>Broadcast boshlandi...</b>\n\n"
        f"Jami: <b>{len(targets)}</b> ta foydalanuvchi"
    )

    sent = failed = 0
    for u in targets:
        try:
            await message.copy_to(chat_id=u["telegram_id"])
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)

    await progress.edit_text(
        f"{em.eRK()} <b>Broadcast yakunlandi!</b>\n\n"
        f"{em.eOK()} Yuborildi: <b>{sent}</b>\n"
        f"❌ Xato: <b>{failed}</b>\n"
        f"{em.eUS()} Jami: <b>{sent + failed}</b>",
        reply_markup=menus.admin_menu(),
    )
