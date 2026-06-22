"""
Asosiy menyu bo'limlari (raw API — premium emoji + rangli inline tugmalar).
Har bir bo'lim skrinshотlardagi dizaynга mos.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards import reply, menus
from app.raw_api import send_message, edit_message, answer_callback, delete_message
from app import emoji as em
from app.config import config

router = Router(name="menu")


# ═══════════════════════════════════════════════════════════════════
# AKKAUNT PANEL MATNI (Image 1) — yordamchi
# ═══════════════════════════════════════════════════════════════════

async def account_panel_text(account) -> str:
    s = await db.get_autosend(account["id"])
    gc = await db.count_groups(account["id"])
    name = account["account_name"] or account["phone"] or f"#{account['id']}"
    status = "🟢 Ishlamoqda" if s["is_running"] else f"{em.emoji('RED')} O'chiq"
    msg_type = {"text": "Matn", "photo": "Rasm+matn", "button": "Tugmali"}.get(
        s["message_type"], "Matn")
    auto_del = "♾ Cheksiz" if s["auto_delete_sec"] == 0 else f"{s['auto_delete_sec']}s"
    mention = "Yoqilgan" if s["mention_enabled"] else "O'chiq"

    return (
        f"{em.emoji('USER')} <b>Boshqaruv panel</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{em.emoji('USERS')} Profil: <b>{name}</b>\n"
        f"{em.emoji('RED')} Holat: <b>{status}</b>\n"
        f"{em.emoji('USER')} Xabar turi: <b>{msg_type}</b>\n"
        f"{em.emoji('CHAT')} Guruhlar: <b>{gc}</b>\n"
        f"{em.emoji('CLOCK')} Interval: <b>{s['interval_min']} daqiqa</b>\n"
        f"{em.emoji('TIMER')} Avto-o'chish: <b>{auto_del}</b>\n"
        f"{em.emoji('MENTION')} Mention: <b>{mention}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )


async def _first_account(user_id: int):
    """Foydalanuvchining birinchi akkauntini qaytaradi (yoki None)."""
    accounts = await db.get_accounts(user_id)
    return accounts[0] if accounts else None


# ═══════════════════════════════════════════════════════════════════
# 1. AUTOHABAR YUBORISH (Image 1)
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text.contains("Autohabar yuborish"))
async def m_autosend(message: Message, state: FSMContext):
    await state.clear()
    account = await _first_account(message.from_user.id)
    if not account:
        await send_message(
            message.from_user.id,
            f"{em.emoji('WARN')} <b>Avval profil (akkaunt) qo'shing!</b>\n\n"
            f"«👥 Profillar» bo'limiga o'tib, akkaunt ulang.",
        )
        return
    s = await db.get_autosend(account["id"])
    await send_message(
        message.from_user.id,
        await account_panel_text(account),
        reply_markup=menus.account_panel(account["id"], s["is_running"], s["mention_enabled"]),
    )


# ═══════════════════════════════════════════════════════════════════
# 2. HABAR MATNI (Image 2)
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text.contains("Habar matni"))
async def m_message(message: Message, state: FSMContext):
    await state.clear()
    account = await _first_account(message.from_user.id)
    if not account:
        await send_message(
            message.from_user.id,
            f"{em.emoji('WARN')} Avval «👥 Profillar» dan akkaunt qo'shing.",
        )
        return
    s = await db.get_autosend(account["id"])
    cur_type = {"text": "Matn", "photo": "Rasm+matn", "button": "Tugmali"}.get(
        s["message_type"], "Matn")
    has_msg = f"{em.emoji('OK')} Sozlangan" if s["message_text"] else f"{em.emoji('RED')} Sozlanmagan"
    text = (
        f"{em.emoji('USER')} <b>Habarni sozlash</b>\n\n"
        f"📄 Joriy tur: <b>{cur_type}</b>\n"
        f"📝 Xabar: <b>{has_msg}</b>\n\n"
        f"Forward faqat Pro tarifda {em.emoji('CARD')}\n\n"
        f"👇 <b>Xabar turini tanlang:</b>"
    )
    await send_message(message.from_user.id, text,
                       reply_markup=menus.message_type_kb(account["id"]))


# ═══════════════════════════════════════════════════════════════════
# 3. INTERVAL (Image 3)
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text.contains("Interval"))
async def m_interval(message: Message, state: FSMContext):
    await state.clear()
    account = await _first_account(message.from_user.id)
    if not account:
        await send_message(message.from_user.id,
                           f"{em.emoji('WARN')} Avval «👥 Profillar» dan akkaunt qo'shing.")
        return
    s = await db.get_autosend(account["id"])
    text = (
        f"{em.emoji('TIMER')} <b>Habar oralig'i</b>\n\n"
        f"Joriy interval: <b>{s['interval_min']} daqiqa</b>\n\n"
        f"Kerakli vaqtni tanlang:"
    )
    await send_message(message.from_user.id, text,
                       reply_markup=menus.interval_kb(account["id"], s["interval_min"]))


# ═══════════════════════════════════════════════════════════════════
# 4. GURUHLARNI SOZLASH (Image 4)
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text.contains("Guruhlarni sozlash"))
async def m_groups(message: Message, state: FSMContext):
    await state.clear()
    account = await _first_account(message.from_user.id)
    if not account:
        await send_message(message.from_user.id,
                           f"{em.emoji('WARN')} Avval «👥 Profillar» dan akkaunt qo'shing.")
        return
    gc = await db.count_groups(account["id"])
    enabled = len(await db.get_enabled_groups(account["id"]))
    choice = "Hamma guruhlarga" if enabled == gc and gc > 0 else f"{enabled} ta tanlangan"
    text = (
        f"{em.emoji('TARGET')} <b>Guruhlarni sozlash</b>\n\n"
        f"Qaysi guruhlarga xabar yuboramiz?\n"
        f"{em.emoji('CHECK')} Tanlangan\n"
        f"➕ Tanlanmagan\n\n"
        f"{em.emoji('PIN')} Hozirgi tanlov: <b>{choice}</b>\n\n"
        f"🗒 <b>Guruhlarni tanlang</b>"
    )
    await send_message(message.from_user.id, text,
                       reply_markup=menus.groups_choice_kb(account["id"]))


# ═══════════════════════════════════════════════════════════════════
# 5. PROFILLAR (akkauntlar)
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text.contains("Profillar"))
async def m_profiles(message: Message, state: FSMContext):
    await state.clear()
    accounts = await db.get_accounts(message.from_user.id)
    text = (
        f"{em.emoji('USERS')} <b>Profillar</b>\n\n"
        + (f"Ulangan akkauntlar: <b>{len(accounts)}</b> ta\n\nBoshqarish uchun tanlang:"
           if accounts else
           "Hali akkaunt ulanmagan.\n\n➕ Akkaunt qo'shish tugmasini bosing.")
    )
    await send_message(message.from_user.id, text,
                       reply_markup=menus.accounts_menu(accounts))


# ═══════════════════════════════════════════════════════════════════
# 6. PRO TARIF (karta + stars + sovg'a)
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text.contains("Pro tarif"))
async def m_pro(message: Message, state: FSMContext):
    await state.clear()
    user = await db.get_user(message.from_user.id)
    is_prem = user["is_premium"] if user else False
    price_card = await db.get_setting("pro_price_card", "50000")
    price_stars = await db.get_setting("pro_price_stars", "500")
    status = f"{em.emoji('CROWN')} <b>Premium faol</b>" if is_prem else "Oddiy (bepul)"
    text = (
        f"{em.emoji('CROWN')} <b>Pro tarif</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Tarifingiz: {status}\n\n"
        f"<b>Pro imkoniyatlari:</b>\n"
        f"{em.emoji('OK')} Cheksiz guruhlar\n"
        f"{em.emoji('OK')} Minimal interval (1 daqiqa)\n"
        f"{em.emoji('OK')} Forward va tugmali xabarlar\n"
        f"{em.emoji('OK')} Bir nechta profil\n\n"
        f"💳 Karta: <b>{int(price_card):,} so'm</b>\n"
        f"⭐️ Stars: <b>{price_stars} ⭐</b>\n\n"
        f"{em.emoji('GIFT')} Boshqaga ham sovg'a qila olasiz!"
    )
    await send_message(message.from_user.id, text,
                       reply_markup=menus.pro_kb(is_prem))


# ═══════════════════════════════════════════════════════════════════
# 7. KABINET (Image 5)
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text.contains("Kabinet"))
async def m_cabinet(message: Message, state: FSMContext):
    await state.clear()
    user = await db.get_user(message.from_user.id)
    accounts = await db.get_accounts(message.from_user.id)
    is_prem = user["is_premium"] if user else False

    # Statistika (barcha akkauntlar bo'yicha)
    total_sent = total_today = total_groups = 0
    interval = 5
    for a in accounts:
        st = await db.get_stats(a["id"])
        total_sent += st["sent"]
        total_today += st["today"]
        total_groups += await db.count_groups(a["id"])
        s = await db.get_autosend(a["id"])
        interval = s["interval_min"]

    first = accounts[0] if accounts else None
    name = first["account_name"] if first else (user["full_name"] if user else "—")
    phone = first["phone"] if first else "—"
    uname = f"@{first['account_username']}" if first and first["account_username"] else "—"

    text = (
        f"{em.emoji('USER')} <b>Sizning Kabinetingiz</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{em.emoji('USERS')} Ism: <b>{name}</b>\n"
        f"📞 Raqam: <code>{phone}</code>\n"
        f"@ Username: <b>{uname}</b>\n\n"
        f"{em.emoji('STATS')} <b>Statistika:</b>\n"
        f"{em.emoji('OK')} Bugun yuborildi: <b>{total_today}</b>\n"
        f"🔄 Jami yuborilgan: <b>{total_sent}</b>\n"
        f"📤 Guruhlar: <b>{total_groups}</b>\n"
        f"{em.emoji('USERS')} Jami profillar: <b>{len(accounts)}</b>\n\n"
        f"⭐ Tarif: <b>{'Premium' if is_prem else 'Free'}</b>\n"
        f"{em.emoji('CROWN')} Premium: <b>{'Bor' if is_prem else 'Pro yo''q'}</b>\n"
        f"{em.emoji('CLOCK')} Interval: <b>{interval} daqiqa</b>"
    )
    await send_message(message.from_user.id, text,
                       reply_markup=menus.cabinet_kb(first["id"] if first else 0))


# ═══════════════════════════════════════════════════════════════════
# 8. SOZLAMALAR (Image 6 — reply keyboard)
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text.contains("Sozlamalar"))
async def m_settings(message: Message, state: FSMContext):
    await state.clear()
    text = (
        f"{em.emoji('GEAR')} <b>Umumiy sozlamalar</b>\n\n"
        f"Qaysi sozlamani o'zgartirmoqchisiz?\n\n"
        f"<i>Bu yerdagi sozlamalar botning umumiy ishlash tartibiga ta'sir qiladi.</i>"
    )
    await send_message(message.from_user.id, text,
                       reply_markup=menus.settings_reply())


# ─── Sozlamalar ichidagi reply tugmalar ─────────────────────────────
@router.message(F.text.contains("Har bir habar oraligi"))
async def m_set_interval(message: Message, state: FSMContext):
    await m_interval(message, state)


@router.message(F.text == "DM javob")
async def m_set_dm(message: Message, state: FSMContext):
    await m_autoreply(message, state)


@router.message(F.text.contains("Avtomatik obuna"))
async def m_set_autosub(message: Message, state: FSMContext):
    await send_message(
        message.from_user.id,
        f"{em.emoji('REFRESH')} <b>Avtomatik obuna</b>\n\n"
        f"Akkaunt ulanganda kerakli kanallarga avtomatik obuna bo'lish.\n\n"
        f"<i>Tez orada qo'shiladi.</i>",
    )


@router.message(F.text.contains("Orqaga"))
async def m_back(message: Message, state: FSMContext):
    await state.clear()
    user = await db.get_user(message.from_user.id)
    if not user:
        user = await db.get_or_create_user(
            message.from_user.id, message.from_user.username or "",
            message.from_user.full_name or "")
    from app.handlers.start import show_main_menu
    await show_main_menu(message.from_user.id, user)


# ═══════════════════════════════════════════════════════════════════
# 9. KALENDAR
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text.contains("Kalendar"))
async def m_calendar(message: Message, state: FSMContext):
    await state.clear()
    await send_message(
        message.from_user.id,
        f"{em.emoji('CALENDAR')} <b>Kalendar</b>\n\n"
        f"Xabar yuborish jadvalini (kunlar/soatlar) sozlash.\n\n"
        f"<i>Tez orada ishga tushadi.</i>",
    )


# ═══════════════════════════════════════════════════════════════════
# 10. FOYDALI FUNKSIYALAR
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text.contains("Foydali funksiyalar"))
async def m_tools(message: Message, state: FSMContext):
    await state.clear()
    await send_message(
        message.from_user.id,
        f"{em.emoji('TOOLS')} <b>Foydali funksiyalar</b>\n\n"
        f"Qo'shimcha vositalar.\n\n<i>Tez orada qo'shiladi.</i>",
    )


# ═══════════════════════════════════════════════════════════════════
# 11. STATISTIKA
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text.contains("Statistika"))
async def m_stats(message: Message, state: FSMContext):
    await state.clear()
    accounts = await db.get_accounts(message.from_user.id)
    if not accounts:
        await send_message(message.from_user.id,
                           f"{em.emoji('STATS')} <b>Statistika</b>\n\nHali ma'lumot yo'q.")
        return
    text = f"{em.emoji('STATS')} <b>Statistika</b>\n━━━━━━━━━━━━━━━━━━━━\n"
    for a in accounts:
        st = await db.get_stats(a["id"])
        gc = await db.count_groups(a["id"])
        name = a["account_name"] or a["phone"]
        text += (
            f"\n{em.emoji('USER')} <b>{name}</b>\n"
            f"   {em.emoji('CHAT')} Guruhlar: <b>{gc}</b>\n"
            f"   {em.emoji('OK')} Yuborilgan: <b>{st['sent']}</b>\n"
            f"   📅 Bugun: <b>{st['today']}</b>\n"
            f"   {em.emoji('CROSS')} Xato: <b>{st['failed']}</b>\n"
        )
    await send_message(message.from_user.id, text, reply_markup=menus.close_kb())


# ═══════════════════════════════════════════════════════════════════
# 12. YORDAM
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text.contains("Yordam"))
async def m_help(message: Message, state: FSMContext):
    await state.clear()
    await send_message(
        message.from_user.id,
        f"{em.emoji('INFO')} <b>Yordam</b>\n\n"
        f"{em.emoji('ROCKET')} <b>Bot nima qiladi?</b>\n"
        f"Akkauntingiz nomidan guruhlarga avtomatik xabar yuboradi.\n\n"
        f"<b>Qadamlar:</b>\n"
        f"1. «👥 Profillar» → Akkaunt qo'shing\n"
        f"2. «💬 Guruhlarni sozlash» → Guruhlarni tanlang\n"
        f"3. «📝 Habar matni» → Xabarni yozing\n"
        f"4. «⏰ Interval» → Vaqtni belgilang\n"
        f"5. «🚀 Autohabar yuborish» → Ishga tushuring\n\n"
        f"❓ @{config.admin_username}",
        reply_markup=menus.close_kb(),
    )


# ═══════════════════════════════════════════════════════════════════
# 13. QO'LLANMA
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text.contains("Qo'llanma"))
async def m_guide(message: Message, state: FSMContext):
    await state.clear()
    await send_message(
        message.from_user.id,
        f"{em.emoji('BOOK')} <b>Qo'llanma</b>\n\n"
        f"{em.emoji('USER')} <b>Akkaunt qo'shish:</b>\n"
        f"«Profillar» → «Akkaunt qo'shish» → QR yoki SMS\n\n"
        f"{em.emoji('CHAT')} <b>Guruhlar:</b>\n"
        f"Akkaunt ulangach avtomatik yuklanadi\n\n"
        f"{em.emoji('EDIT')} <b>Xabar:</b>\n"
        f"Har bir profil uchun alohida matn\n\n"
        f"{em.emoji('CLOCK')} <b>Interval:</b> 2 daqiqadan 3 soatgacha\n\n"
        f"<i>Batafsil: @{config.admin_username}</i>",
        reply_markup=menus.close_kb(),
    )


# ═══════════════════════════════════════════════════════════════════
# 14. AUTOREPLY
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text.contains("Autoreply"))
async def m_autoreply(message: Message, state: FSMContext):
    await state.clear()
    account = await _first_account(message.from_user.id)
    if not account:
        await send_message(message.from_user.id,
                           f"{em.emoji('WARN')} Avval «👥 Profillar» dan akkaunt qo'shing.")
        return
    r = await db.get_autoreply(account["id"])
    status = "🟢 Yoqilgan" if r["is_enabled"] else f"{em.emoji('RED')} O'chiq"
    cur = r["reply_text"] or "(yo'q)"
    text = (
        f"{em.emoji('CHAT')} <b>Autoreply (DM avto-javob)</b>\n\n"
        f"Holat: <b>{status}</b>\n\n"
        f"Javob matni:\n<blockquote>{cur[:300]}</blockquote>\n\n"
        f"Siz onlayn bo'lmaganda kelgan shaxsiy xabarlarga avtomatik javob beradi."
    )
    await send_message(message.from_user.id, text,
                       reply_markup=menus.autoreply_kb(account["id"], r["is_enabled"]))


# ═══════════════════════════════════════════════════════════════════
# UMUMIY CALLBACK — yopish va asosiy menyu
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data == "close_msg")
async def cb_close(call: CallbackQuery):
    try:
        await delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    await answer_callback(call.id)


@router.callback_query(F.data == "profiles_back")
async def cb_profiles_back(call: CallbackQuery, state: FSMContext):
    await state.clear()
    from app.userbot import login
    await login.cancel_login(call.from_user.id)
    accounts = await db.get_accounts(call.from_user.id)
    text = (
        f"{em.emoji('USERS')} <b>Profillar</b>\n\n"
        + (f"Ulangan: <b>{len(accounts)}</b> ta" if accounts else "Hali akkaunt yo'q.")
    )
    await edit_message(call.message.chat.id, call.message.message_id, text,
                       reply_markup=menus.accounts_menu(accounts))
    await answer_callback(call.id)


@router.callback_query(F.data == "back_main")
async def cb_back_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    user = await db.get_user(call.from_user.id)
    if not user:
        user = await db.get_or_create_user(
            call.from_user.id, call.from_user.username or "",
            call.from_user.full_name or "")
    from app.handlers.start import show_main_menu
    await show_main_menu(call.from_user.id, user)
    await answer_callback(call.id)
