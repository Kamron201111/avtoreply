"""
Admin panel — raw API bilan.
Statistika, foydalanuvchilar, premium, broadcast, Pro narx/karta sozlash.
"""
import asyncio

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards import menus
from app.raw_api import send_message, edit_message, answer_callback
from app.states import AdminStates
from app import emoji as em
from app.config import config

router = Router(name="admin")


def _adm(uid: int) -> bool:
    return config.is_admin(uid)


@router.callback_query(F.data == "adm_main")
async def cb_main(call: CallbackQuery, state: FSMContext):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    await state.clear()
    await edit_message(call.message.chat.id, call.message.message_id,
                       f"{em.emoji('GEAR')} <b>Admin panel</b>", reply_markup=menus.admin_menu())
    await answer_callback(call.id)


@router.callback_query(F.data == "adm_stats")
async def cb_stats(call: CallbackQuery):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    st = await db.get_global_stats()
    text = (
        f"{em.emoji('STATS')} <b>Umumiy statistika</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{em.emoji('USERS')} Foydalanuvchilar: <b>{st['users']}</b>\n"
        f"{em.emoji('PHONE')} Profillar: <b>{st['accounts']}</b>\n"
        f"🟢 Faol: <b>{st['active']}</b>\n"
        f"{em.emoji('CHAT')} Guruhlar: <b>{st['groups']}</b>\n"
        f"{em.emoji('OK')} Yuborilgan: <b>{st['sent_total']}</b>"
    )
    await edit_message(call.message.chat.id, call.message.message_id, text,
                       reply_markup=menus.admin_back())
    await answer_callback(call.id)


@router.callback_query(F.data == "adm_users")
async def cb_users(call: CallbackQuery):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    users = await db.all_users()
    text = f"{em.emoji('USERS')} Jami <b>{len(users)}</b> foydalanuvchi:\n\n"
    for u in users[:30]:
        mark = "🚫" if u["is_banned"] else ("👑" if u["is_premium"] else "✅")
        uname = f"@{u['username']}" if u["username"] else u["full_name"]
        text += f"{mark} <code>{u['telegram_id']}</code> — {uname}\n"
    if len(users) > 30:
        text += f"\n... yana {len(users)-30} ta"
    await edit_message(call.message.chat.id, call.message.message_id, text,
                       reply_markup=menus.admin_back())
    await answer_callback(call.id)


# ─── PREMIUM ────────────────────────────────────────────────────────
@router.callback_query(F.data == "adm_give_premium")
async def cb_give(call: CallbackQuery, state: FSMContext):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    await state.set_state(AdminStates.waiting_premium_id)
    await state.update_data(action="give")
    await edit_message(call.message.chat.id, call.message.message_id,
        f"{em.emoji('OK')} <b>Premium berish</b>\n\nFoydalanuvchi Telegram ID sini yuboring:",
        reply_markup=menus.admin_back())
    await answer_callback(call.id)


@router.callback_query(F.data == "adm_take_premium")
async def cb_take(call: CallbackQuery, state: FSMContext):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    await state.set_state(AdminStates.waiting_premium_id)
    await state.update_data(action="take")
    await edit_message(call.message.chat.id, call.message.message_id,
        f"{em.emoji('WARN')} <b>Premium olish</b>\n\nFoydalanuvchi Telegram ID sini yuboring:",
        reply_markup=menus.admin_back())
    await answer_callback(call.id)


@router.message(AdminStates.waiting_premium_id)
async def on_premium_id(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    data = await state.get_data()
    give = data.get("action") == "give"
    digits = "".join(c for c in message.text if c.isdigit())
    if not digits:
        await message.answer(f"{em.emoji('WARN')} ID faqat raqam.")
        return
    tg_id = int(digits)
    if not await db.get_user(tg_id):
        await message.answer(f"{em.emoji('WARN')} Foydalanuvchi topilmadi.")
        return
    await db.set_premium(tg_id, give)
    await state.clear()
    await send_message(message.from_user.id,
        f"{em.emoji('OK')} <code>{tg_id}</code> premium {'berildi 👑' if give else 'olindi'}!",
        reply_markup=menus.admin_menu())
    try:
        if give:
            await send_message(tg_id, f"{em.emoji('CROWN')} <b>Tabriklaymiz!</b>\n\nSizga <b>Pro</b> tarif berildi! 🎉")
        else:
            await send_message(tg_id, f"{em.emoji('WARN')} Pro tarifingiz tugadi.")
    except Exception:
        pass


# ─── PRO NARXLARI ───────────────────────────────────────────────────
@router.callback_query(F.data == "adm_prices")
async def cb_prices(call: CallbackQuery, state: FSMContext):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    card = await db.get_setting("pro_price_card", "50000")
    stars = await db.get_setting("pro_price_stars", "500")
    await state.set_state(AdminStates.waiting_prices)
    await edit_message(call.message.chat.id, call.message.message_id,
        f"{em.emoji('MONEY')} <b>Pro narxlari</b>\n\n"
        f"💳 Karta: <b>{card}</b> so'm\n"
        f"⭐️ Stars: <b>{stars}</b>\n\n"
        f"Yangi narxlarni shu formatda yuboring:\n"
        f"<code>karta_narx stars_narx</code>\n"
        f"Masalan: <code>50000 500</code>",
        reply_markup=menus.admin_back())
    await answer_callback(call.id)


@router.message(AdminStates.waiting_prices)
async def on_prices(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) != 2 or not all(p.isdigit() for p in parts):
        await message.answer(f"{em.emoji('WARN')} Format: <code>50000 500</code>")
        return
    await db.set_setting("pro_price_card", parts[0])
    await db.set_setting("pro_price_stars", parts[1])
    await state.clear()
    await send_message(message.from_user.id,
        f"{em.emoji('OK')} Narxlar yangilandi!\n💳 {int(parts[0]):,} so'm\n⭐️ {parts[1]} stars",
        reply_markup=menus.admin_menu())


# ─── KARTA RAQAMI ───────────────────────────────────────────────────
@router.callback_query(F.data == "adm_card")
async def cb_card(call: CallbackQuery, state: FSMContext):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    card = await db.get_setting("card_number", "")
    holder = await db.get_setting("card_holder", "")
    await state.set_state(AdminStates.waiting_card)
    await edit_message(call.message.chat.id, call.message.message_id,
        f"{em.emoji('CARD')} <b>Karta raqami</b>\n\n"
        f"Joriy: <code>{card or 'yo''q'}</code>\n"
        f"Egasi: <b>{holder or '—'}</b>\n\n"
        f"Yangi karta ma'lumotini shu formatda yuboring:\n"
        f"<code>8600123456789012 Ism Familiya</code>",
        reply_markup=menus.admin_back())
    await answer_callback(call.id)


@router.message(AdminStates.waiting_card)
async def on_card(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    parts = message.text.strip().split(maxsplit=1)
    card_num = "".join(c for c in parts[0] if c.isdigit())
    if len(card_num) < 16:
        await message.answer(f"{em.emoji('WARN')} Karta raqami noto'g'ri (16 raqam).")
        return
    holder = parts[1] if len(parts) > 1 else ""
    await db.set_setting("card_number", card_num)
    await db.set_setting("card_holder", holder)
    await state.clear()
    await send_message(message.from_user.id,
        f"{em.emoji('OK')} Karta saqlandi!\n💳 <code>{card_num}</code>\n👤 {holder}",
        reply_markup=menus.admin_menu())


# ─── BROADCAST ──────────────────────────────────────────────────────
@router.callback_query(F.data == "adm_broadcast")
async def cb_broadcast(call: CallbackQuery, state: FSMContext):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    await state.set_state(AdminStates.waiting_broadcast)
    await edit_message(call.message.chat.id, call.message.message_id,
        f"{em.emoji('ROCKET')} <b>Broadcast</b>\n\nBarchaga yuboriladigan xabarni yuboring:",
        reply_markup=menus.admin_back())
    await answer_callback(call.id)


@router.message(AdminStates.waiting_broadcast)
async def on_broadcast(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    await state.clear()
    users = await db.all_users()
    targets = [u for u in users if not u["is_banned"]]
    progress = await message.answer(f"{em.emoji('ROCKET')} Yuborilmoqda... 0/{len(targets)}")
    sent = failed = 0
    for u in targets:
        try:
            await message.copy_to(chat_id=u["telegram_id"])
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)
    await progress.edit_text(
        f"{em.emoji('ROCKET')} <b>Yakunlandi!</b>\n"
        f"{em.emoji('OK')} Yuborildi: <b>{sent}</b>\n❌ Xato: <b>{failed}</b>")
