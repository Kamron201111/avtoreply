"""
Admin panel — reply keyboard (pastda) + inline amallar. 3 tilli, to'liq.
"""
import asyncio
import json

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards import menus, reply
from app.keyboards.builder import btn, inline_kb
from app.raw_api import send_message, edit_message, answer_callback
from app.states import AdminStates
from app.i18n import t, is_button
from app.lang_util import get_lang
from app import emoji as em
from app.config import config

router = Router(name="admin")


def _adm(uid):
    return config.is_admin(uid)


def _is_btn(text, key):
    return is_button(text, key)


# ═══════════════════════════════════════════════════════════════════
# ADMIN PANELNI OCHISH (asosiy menyudagi "Admin panel" tugmasi)
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "btn_admin"))
async def open_admin(message: Message, state: FSMContext):
    await state.clear()
    if not _adm(message.from_user.id):
        return
    lang = await get_lang(message.from_user.id)
    await send_message(message.from_user.id,
                       f"{t('adm_title', lang)}\n\n{t('adm_panel_hint', lang)}",
                       reply_markup=reply.admin_menu(lang))


# ═══════════════════════════════════════════════════════════════════
# ADMIN PANELDAN CHIQISH
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "adm_b_exit"))
async def admin_exit(message: Message, state: FSMContext):
    await state.clear()
    if not _adm(message.from_user.id):
        return
    from app.handlers.start import show_main_menu
    await show_main_menu(message.from_user.id)


# ═══════════════════════════════════════════════════════════════════
# 1. STATISTIKA
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "adm_b_stats"))
async def adm_stats(message: Message, state: FSMContext):
    await state.clear()
    if not _adm(message.from_user.id):
        return
    lang = await get_lang(message.from_user.id)
    st = await db.get_global_stats()
    text = (
        f"{em.emoji('STATS')} <b>Statistika</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        f"{em.emoji('USERS')} Foydalanuvchilar: <b>{st['users']}</b>\n"
        f"{em.emoji('CROWN')} Premium: <b>{st['premium']}</b>\n"
        f"{em.emoji('PHONE')} Profillar: <b>{st['accounts']}</b>\n"
        f"🟢 Faol yuborish: <b>{st['active']}</b>\n"
        f"{em.emoji('GROUP')} Guruhlar: <b>{st['groups']}</b>\n"
        f"{em.emoji('OK')} Yuborilgan: <b>{st['sent_total']}</b>"
    )
    await send_message(message.from_user.id, text)


# ═══════════════════════════════════════════════════════════════════
# 2. FOYDALANUVCHILAR
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "adm_b_users"))
async def adm_users(message: Message, state: FSMContext):
    await state.clear()
    if not _adm(message.from_user.id):
        return
    users = await db.all_users()
    text = f"{em.emoji('USERS')} Jami <b>{len(users)}</b> foydalanuvchi:\n\n"
    for u in users[:40]:
        mark = "🚫" if u["is_banned"] else ("👑" if u["is_premium"] else "✅")
        uname = f"@{u['username']}" if u["username"] else u["full_name"]
        text += f"{mark} <code>{u['telegram_id']}</code> {uname}\n"
    if len(users) > 40:
        text += f"\n... +{len(users)-40}"
    await send_message(message.from_user.id, text)


# ═══════════════════════════════════════════════════════════════════
# 3-4. PREMIUM BERISH / OLISH
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "adm_b_give"))
async def adm_give(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    await state.set_state(AdminStates.waiting_premium_id)
    await state.update_data(action="give")
    await send_message(message.from_user.id,
                       f"{em.emoji('OK')} <b>Premium berish</b>\n\nFoydalanuvchi ID raqamini yuboring:",
                       reply_markup=_cancel_inline())


@router.message(lambda m: _is_btn(m.text, "adm_b_take"))
async def adm_take(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    await state.set_state(AdminStates.waiting_premium_id)
    await state.update_data(action="take")
    await send_message(message.from_user.id,
                       f"{em.emoji('WARN')} <b>Premium olish</b>\n\nFoydalanuvchi ID raqamini yuboring:",
                       reply_markup=_cancel_inline())


@router.message(AdminStates.waiting_premium_id)
async def on_premium_id(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    lang = await get_lang(message.from_user.id)
    data = await state.get_data()
    give = data.get("action") == "give"
    digits = "".join(c for c in message.text if c.isdigit())
    if not digits:
        await message.answer("❌ ID faqat raqam bo'lishi kerak.")
        return
    tg_id = int(digits)
    if not await db.get_user(tg_id):
        await message.answer("❌ Bunday foydalanuvchi topilmadi (u /start bosishi kerak).")
        return
    await db.set_premium(tg_id, give)
    await state.clear()
    await send_message(message.from_user.id,
                       f"{em.emoji('OK')} <code>{tg_id}</code> uchun Premium {'berildi 👑' if give else 'olindi'}!",
                       reply_markup=reply.admin_menu(lang))
    try:
        tlang = await get_lang(tg_id)
        await send_message(tg_id, t("pro_granted", tlang) if give else "⚠️ Pro tarifingiz tugadi.")
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════
# 5. PRO NARXLARI
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "adm_b_prices"))
async def adm_prices(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    card = await db.get_setting("pro_price_card", "50000")
    stars = await db.get_setting("pro_price_stars", "500")
    await state.set_state(AdminStates.waiting_prices)
    await send_message(message.from_user.id,
                       f"{em.emoji('MONEY')} <b>Pro narxlari</b>\n\n"
                       f"💳 Karta: <b>{card}</b> so'm\n⭐️ Stars: <b>{stars}</b>\n\n"
                       f"Yangi narxni shu formatda yuboring:\n<code>karta_narx stars_narx</code>\n"
                       f"Masalan: <code>50000 500</code>",
                       reply_markup=_cancel_inline())


@router.message(AdminStates.waiting_prices)
async def on_prices(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    lang = await get_lang(message.from_user.id)
    parts = message.text.split()
    if len(parts) != 2 or not all(p.isdigit() for p in parts):
        await message.answer("❌ Format noto'g'ri. Masalan: <code>50000 500</code>")
        return
    await db.set_setting("pro_price_card", parts[0])
    await db.set_setting("pro_price_stars", parts[1])
    await state.clear()
    await send_message(message.from_user.id,
                       f"{em.emoji('OK')} Narxlar yangilandi!\n💳 {int(parts[0]):,} so'm\n⭐️ {parts[1]} stars",
                       reply_markup=reply.admin_menu(lang))


# ═══════════════════════════════════════════════════════════════════
# 6. KARTA RAQAMI
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "adm_b_card"))
async def adm_card(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    card = await db.get_setting("card_number", "")
    holder = await db.get_setting("card_holder", "")
    await state.set_state(AdminStates.waiting_card)
    await send_message(message.from_user.id,
                       f"{em.emoji('CARD')} <b>Karta raqami</b>\n\n"
                       f"Joriy karta: <code>{card or 'kiritilmagan'}</code>\n"
                       f"Egasi: <b>{holder or '—'}</b>\n\n"
                       f"Yangi kartani shu formatda yuboring:\n"
                       f"<code>8600123456789012 Aziz Azizov</code>\n\n"
                       f"<i>(karta raqami va egasining ismi)</i>",
                       reply_markup=_cancel_inline())


@router.message(AdminStates.waiting_card)
async def on_card(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    lang = await get_lang(message.from_user.id)
    raw = (message.text or "").strip()
    parts = raw.split(maxsplit=1)
    if not parts:
        await message.answer("❌ Karta raqamini yuboring.")
        return
    # Birinchi qism — raqamlar (probel bilan ham bo'lishi mumkin)
    card_num = "".join(c for c in parts[0] if c.isdigit())
    # Agar birinchi qismda 16 raqam bo'lmasa, butun matndan raqamlarni olamiz
    if len(card_num) < 16:
        all_digits = "".join(c for c in raw if c.isdigit())
        if len(all_digits) >= 16:
            card_num = all_digits[:16]
            # Ism — raqamlardan keyingi matn
            holder = "".join(c for c in raw if not c.isdigit()).strip()
        else:
            await message.answer("❌ Karta raqami 16 ta raqamdan iborat bo'lishi kerak.\n"
                                 "Masalan: <code>8600123456789012 Aziz Azizov</code>")
            return
    else:
        card_num = card_num[:16]
        holder = parts[1] if len(parts) > 1 else ""
    await db.set_setting("card_number", card_num)
    await db.set_setting("card_holder", holder)
    await state.clear()
    # Chiroyli formatda ko'rsatamiz
    pretty = " ".join(card_num[i:i+4] for i in range(0, 16, 4))
    await send_message(message.from_user.id,
                       f"{em.emoji('OK')} <b>Karta saqlandi!</b>\n\n💳 <code>{pretty}</code>\n👤 {holder or '—'}",
                       reply_markup=reply.admin_menu(lang))


# ═══════════════════════════════════════════════════════════════════
# 7. QO'LLANMA MATNI
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "adm_b_guide"))
async def adm_guide(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    cur = await db.get_setting("guide_uz", "")
    await state.set_state(AdminStates.waiting_guide)
    await send_message(message.from_user.id,
                       f"{em.emoji('BOOK')} <b>Qo'llanma matni</b>\n\n"
                       f"Joriy:\n<blockquote>{cur[:400] or '(kiritilmagan)'}</blockquote>\n\n"
                       f"Yangi qo'llanma matnini yuboring (HTML formatlash mumkin):",
                       reply_markup=_cancel_inline())


@router.message(AdminStates.waiting_guide)
async def on_guide(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    lang = await get_lang(message.from_user.id)
    text = message.html_text or message.text or ""
    for l in ("uz", "ru", "en"):
        await db.set_setting(f"guide_{l}", text)
    await state.clear()
    await send_message(message.from_user.id, f"{em.emoji('OK')} Qo'llanma saqlandi!",
                       reply_markup=reply.admin_menu(lang))


# ═══════════════════════════════════════════════════════════════════
# 8. STATISTIKA TAVSIFI
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "adm_b_statsdesc"))
async def adm_statsdesc(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    cur = await db.get_setting("stats_desc_uz", "")
    await state.set_state(AdminStates.waiting_statsdesc)
    await send_message(message.from_user.id,
                       f"{em.emoji('STATS')} <b>Statistika tavsifi</b>\n\n"
                       f"Joriy:\n<blockquote>{cur[:400] or '(kiritilmagan)'}</blockquote>\n\n"
                       f"Statistika bo'limida ko'rinadigan tavsif matnini yuboring:",
                       reply_markup=_cancel_inline())


@router.message(AdminStates.waiting_statsdesc)
async def on_statsdesc(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    lang = await get_lang(message.from_user.id)
    text = message.html_text or message.text or ""
    for l in ("uz", "ru", "en"):
        await db.set_setting(f"stats_desc_{l}", text)
    await state.clear()
    await send_message(message.from_user.id, f"{em.emoji('OK')} Tavsif saqlandi!",
                       reply_markup=reply.admin_menu(lang))


# ═══════════════════════════════════════════════════════════════════
# 9. YORDAM SOZLASH (kanal/chat/admin)
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "adm_b_help"))
async def adm_help(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    ch = await db.get_setting("help_channel", "")
    chat = await db.get_setting("help_chat", "")
    adm = await db.get_setting("help_admin", "")
    await state.set_state(AdminStates.waiting_help)
    await send_message(message.from_user.id,
                       f"{em.emoji('INFO')} <b>Yordam sozlash</b>\n\n"
                       f"📢 Kanal: {ch or '—'}\n💬 Chat: {chat or '—'}\n👤 Admin: {adm or '—'}\n\n"
                       f"Yangi ma'lumotni shu formatda yuboring:\n"
                       f"<code>@kanal @chat @admin</code>",
                       reply_markup=_cancel_inline())


@router.message(AdminStates.waiting_help)
async def on_help(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    lang = await get_lang(message.from_user.id)
    parts = message.text.split()
    if len(parts) >= 1:
        await db.set_setting("help_channel", parts[0])
    if len(parts) >= 2:
        await db.set_setting("help_chat", parts[1])
    if len(parts) >= 3:
        await db.set_setting("help_admin", parts[2])
    await state.clear()
    await send_message(message.from_user.id, f"{em.emoji('OK')} Yordam ma'lumoti saqlandi!",
                       reply_markup=reply.admin_menu(lang))


# ═══════════════════════════════════════════════════════════════════
# 10. MAJBURIY OBUNA (inline boshqaruv)
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "adm_b_channels"))
async def adm_channels(message: Message, state: FSMContext):
    await state.clear()
    if not _adm(message.from_user.id):
        return
    await _show_channels(message.from_user.id, None)


async def _show_channels(user_id, msg_id):
    lang = await get_lang(user_id)
    channels = await db.get_channels()
    text = f"{em.emoji('CHAT')} <b>Majburiy obuna kanallari</b>\n\n"
    rows = []
    if channels:
        for c in channels:
            text += f"• {c['title']} (<code>{c['channel_id']}</code>)\n"
            rows.append([btn(f"🗑 {c['title'][:20]}", cb=f"chdel_{c['id']}", style="danger")])
    else:
        text += "<i>Hozircha kanal yo'q.</i>\n"
    rows.append([btn("➕ Kanal qo'shish", cb="chadd", icon="OK", style="success")])
    kb = inline_kb(rows)
    if msg_id:
        await edit_message(user_id, msg_id, text, reply_markup=kb)
    else:
        await send_message(user_id, text, reply_markup=kb)


@router.callback_query(F.data == "chadd")
async def cb_chadd(call: CallbackQuery, state: FSMContext):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    await state.set_state(AdminStates.waiting_channel)
    await edit_message(call.message.chat.id, call.message.message_id,
                       f"{em.emoji('CHAT')} <b>Kanal qo'shish</b>\n\n"
                       f"Format: <code>@kanal Kanal nomi</code>\n"
                       f"yoki ID bilan: <code>-1001234567890 Nomi</code>",
                       reply_markup=inline_kb([[btn("Bekor", cb="chback", icon="BACK", style="danger")]]))
    await answer_callback(call.id)


@router.message(AdminStates.waiting_channel)
async def on_channel(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    parts = message.text.strip().split(maxsplit=1)
    ch_id = parts[0]
    title = parts[1] if len(parts) > 1 else ch_id
    invite = f"https://t.me/{ch_id.lstrip('@')}" if ch_id.startswith("@") else ""
    await db.add_channel(ch_id, title, invite)
    await state.clear()
    await send_message(message.from_user.id, f"{em.emoji('OK')} Kanal qo'shildi: <b>{title}</b>")
    await _show_channels(message.from_user.id, None)


@router.callback_query(F.data == "chback")
async def cb_chback(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await _show_channels(call.from_user.id, call.message.message_id)
    await answer_callback(call.id)


@router.callback_query(F.data.startswith("chdel_"))
async def cb_chdel(call: CallbackQuery):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    ch_id = int(call.data.split("_")[1])
    await db.remove_channel(ch_id)
    await answer_callback(call.id, "🗑 O'chirildi", show_alert=True)
    await _show_channels(call.from_user.id, call.message.message_id)


# ═══════════════════════════════════════════════════════════════════
# 11. MUROJATLAR (ikki tomonlama javob)
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "adm_b_tickets"))
async def adm_tickets(message: Message, state: FSMContext):
    await state.clear()
    if not _adm(message.from_user.id):
        return
    async with db.pool().acquire() as con:
        tickets = await con.fetch("SELECT * FROM tickets WHERE status='open' ORDER BY id DESC LIMIT 10")
    if not tickets:
        await send_message(message.from_user.id,
                           f"{em.emoji('REPLY')} <b>Murojatlar</b>\n\nYangi murojat yo'q.")
        return
    text = f"{em.emoji('REPLY')} <b>Ochiq murojatlar:</b>\n\n"
    rows = []
    for tk in tickets:
        text += f"<b>#{tk['id']}</b> {tk['username']}:\n<blockquote>{tk['message'][:100]}</blockquote>\n"
        rows.append([btn(f"✍️ #{tk['id']} javob berish", cb=f"ticket_reply_{tk['user_id']}_{tk['id']}", style="success")])
    await send_message(message.from_user.id, text, reply_markup=inline_kb(rows))


@router.callback_query(F.data.startswith("ticket_reply_"))
async def cb_ticket_reply(call: CallbackQuery, state: FSMContext):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    parts = call.data.split("_")
    user_id = int(parts[2])
    ticket_id = int(parts[3]) if len(parts) > 3 else 0
    await state.set_state(AdminStates.waiting_ticket_reply)
    await state.update_data(ticket_user=user_id, ticket_id=ticket_id)
    await send_message(call.from_user.id,
                       f"✍️ <code>{user_id}</code> ga javobingizni yozing:")
    await answer_callback(call.id)


@router.message(AdminStates.waiting_ticket_reply)
async def on_ticket_reply(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    lang = await get_lang(message.from_user.id)
    data = await state.get_data()
    user_id = data.get("ticket_user")
    ticket_id = data.get("ticket_id", 0)
    await state.clear()
    if not user_id:
        return
    reply_text = message.html_text or message.text or ""
    try:
        tlang = await get_lang(user_id)
        await send_message(user_id,
                           f"{em.emoji('REPLY')} <b>Admin javobi:</b>\n\n{reply_text}")
        if ticket_id:
            await db.close_ticket(ticket_id)
        await send_message(message.from_user.id, f"{em.emoji('OK')} Javob yuborildi!",
                           reply_markup=reply.admin_menu(lang))
    except Exception:
        await send_message(message.from_user.id, "❌ Yuborilmadi (foydalanuvchi botni bloklagan bo'lishi mumkin).",
                           reply_markup=reply.admin_menu(lang))


# ═══════════════════════════════════════════════════════════════════
# 12. BROADCAST
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "adm_b_broadcast"))
async def adm_broadcast(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    await state.set_state(AdminStates.waiting_broadcast)
    await send_message(message.from_user.id,
                       f"{em.emoji('ROCKET')} <b>Broadcast</b>\n\n"
                       f"Barcha foydalanuvchilarga yuboriladigan xabarni yuboring.\n"
                       f"<i>(matn, rasm, video — hammasi mumkin)</i>",
                       reply_markup=_cancel_inline())


@router.message(AdminStates.waiting_broadcast)
async def on_broadcast(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    lang = await get_lang(message.from_user.id)
    await state.clear()
    users = await db.all_users()
    targets = [u for u in users if not u["is_banned"]]
    prog = await message.answer(f"{em.emoji('ROCKET')} Yuborilmoqda... 0/{len(targets)}")
    sent = failed = 0
    for u in targets:
        try:
            await message.copy_to(chat_id=u["telegram_id"])
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)
    await prog.edit_text(f"{em.emoji('OK')} <b>Yakunlandi!</b>\n✅ Yuborildi: {sent}\n❌ Xato: {failed}")
    await send_message(message.from_user.id, t("adm_title", lang),
                       reply_markup=reply.admin_menu(lang))


# ═══════════════════════════════════════════════════════════════════
# Umumiy: bekor qilish (state'ni tozalab admin panelga qaytadi)
# ═══════════════════════════════════════════════════════════════════
def _cancel_inline():
    return inline_kb([[btn("Bekor qilish", cb="adm_cancel", icon="BACK", style="danger")]])


@router.callback_query(F.data == "adm_cancel")
async def cb_adm_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await edit_message(call.message.chat.id, call.message.message_id,
                           f"{em.emoji('OK')} Bekor qilindi.")
    except Exception:
        pass
    await answer_callback(call.id)
