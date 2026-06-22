"""
Asosiy menyu tugmalari handleri (ReplyKeyboard tugmalari).

Har bir pastdagi tugma bosilganda mos bo'lim ochiladi.
HOZIRCHA har bir bo'lim oddiy javob beradi — keyin har birini alohida to'ldiramiz.
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards import reply
from app import emoji as em
from app.config import config

router = Router(name="menu")


# ═══════════════════════════════════════════════════════════════════
# 1. AUTOHABAR YUBORISH
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text == reply.BTN_AUTOSEND)
async def m_autosend(message: Message, state: FSMContext):
    await state.clear()
    accounts = await db.get_accounts(message.from_user.id)
    if not accounts:
        await message.answer(
            f"{em.pe('warn')} <b>Avval akkaunt qo'shing!</b>\n\n"
            f"Autohabar yuborish uchun kamida bitta akkaunt ulashingiz kerak.\n"
            f"«{em.oe('user')} Profillar» bo'limiga o'ting va akkaunt qo'shing."
        )
        return
    text = f"{em.pe('rocket')} <b>Autohabar yuborish</b>\n\n"
    for a in accounts:
        s = await db.get_autosend(a["id"])
        status = "🟢 Ishlamoqda" if s["is_running"] else "🔴 To'xtagan"
        name = a["account_name"] or a["phone"]
        text += f"{em.pe('user')} <b>{name}</b> — {status}\n"
    text += f"\n<i>Boshqarish uchun «Profillar» bo'limidan akkauntni tanlang.</i>"
    await message.answer(text)


# ═══════════════════════════════════════════════════════════════════
# 2. HABAR MATNI
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text == reply.BTN_MESSAGE)
async def m_message(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"{em.pe('edit')} <b>Habar matni</b>\n\n"
        f"Bu bo'limda guruhlarga yuboriladigan xabar matnini sozlaysiz.\n\n"
        f"<i>Akkauntni «Profillar» dan tanlab, har biri uchun alohida "
        f"xabar matni o'rnatishingiz mumkin.</i>"
    )


# ═══════════════════════════════════════════════════════════════════
# 3. INTERVAL
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text == reply.BTN_INTERVAL)
async def m_interval(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"{em.pe('clock')} <b>Interval (xabar oralig'i)</b>\n\n"
        f"Bu bo'limda xabarlar qancha vaqtda bir yuborilishini sozlaysiz.\n\n"
        f"<i>Akkauntni «Profillar» dan tanlab, intervalni o'rnating.</i>"
    )


# ═══════════════════════════════════════════════════════════════════
# 4. GURUHLARNI SOZLASH
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text == reply.BTN_GROUPS)
async def m_groups(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"{em.pe('chat')} <b>Guruhlarni sozlash</b>\n\n"
        f"Bu bo'limda xabar yuboriladigan guruhlarni tanlaysiz.\n\n"
        f"<i>Akkauntni «Profillar» dan tanlab, guruhlarni yoqing/o'chiring.</i>"
    )


# ═══════════════════════════════════════════════════════════════════
# 5. PROFILLAR (akkauntlar)
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text == reply.BTN_PROFILES)
async def m_profiles(message: Message, state: FSMContext):
    await state.clear()
    # Bu yerda inline menyu ishlatamiz (akkaunt boshqaruvi uchun qulay)
    from app.keyboards import menus
    accounts = await db.get_accounts(message.from_user.id)
    text = (
        f"{em.pe('user')} <b>Profillar (akkauntlar)</b>\n\n"
        + (f"Ulangan akkauntlar: <b>{len(accounts)}</b> ta\n\nBoshqarish uchun tanlang:"
           if accounts else
           "Hali akkaunt ulanmagan.\n\n➕ Akkaunt qo'shish tugmasini bosing.")
    )
    await message.answer(text, reply_markup=menus.accounts_menu(accounts))


# ═══════════════════════════════════════════════════════════════════
# 6. PRO TARIF
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text == reply.BTN_PRO)
async def m_pro(message: Message, state: FSMContext):
    await state.clear()
    user = await db.get_user(message.from_user.id)
    is_prem = user["is_premium"] if user else False
    status = f"{em.pe('crown')} <b>Premium faol</b>" if is_prem else "Oddiy (bepul)"
    await message.answer(
        f"{em.pe('crown')} <b>Pro tarif</b>\n\n"
        f"Sizning tarifingiz: {status}\n\n"
        f"<b>Pro tarif imkoniyatlari:</b>\n"
        f"• Cheksiz guruhlar\n"
        f"• Minimal interval (1 daqiqa)\n"
        f"• Bir nechta akkaunt\n"
        f"• Ustuvor qo'llab-quvvatlash\n\n"
        f"<i>Sotib olish uchun: @{config.admin_username}</i>"
    )


# ═══════════════════════════════════════════════════════════════════
# 7. KABINET
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text == reply.BTN_CABINET)
async def m_cabinet(message: Message, state: FSMContext):
    await state.clear()
    user = await db.get_user(message.from_user.id)
    accounts = await db.get_accounts(message.from_user.id)
    is_prem = user["is_premium"] if user else False
    await message.answer(
        f"{em.pe('user')} <b>Kabinet</b>\n\n"
        f"{em.pe('info')} ID: <code>{message.from_user.id}</code>\n"
        f"{em.pe('user')} Ism: <b>{user['full_name'] if user else '—'}</b>\n"
        f"{em.pe('crown')} Tarif: <b>{'Premium' if is_prem else 'Oddiy'}</b>\n"
        f"{em.pe('user')} Akkauntlar: <b>{len(accounts)}</b> ta\n"
    )


# ═══════════════════════════════════════════════════════════════════
# 8. SOZLAMALAR
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text == reply.BTN_SETTINGS)
async def m_settings(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"{em.pe('gear')} <b>Sozlamalar</b>\n\n"
        f"Bu bo'limda bot sozlamalarini o'zgartirasiz.\n\n"
        f"<i>Tez orada qo'shimcha sozlamalar qo'shiladi.</i>"
    )


# ═══════════════════════════════════════════════════════════════════
# 9. KALENDAR
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text == reply.BTN_CALENDAR)
async def m_calendar(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"{em.pe('clock')} <b>Kalendar</b>\n\n"
        f"Bu bo'limda xabar yuborish jadvalini (kunlar/soatlar) sozlaysiz.\n\n"
        f"<i>Tez orada ishga tushadi.</i>"
    )


# ═══════════════════════════════════════════════════════════════════
# 10. FOYDALI FUNKSIYALAR
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text == reply.BTN_TOOLS)
async def m_tools(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"{em.pe('gear')} <b>Foydali funksiyalar</b>\n\n"
        f"Qo'shimcha vositalar va imkoniyatlar.\n\n"
        f"<i>Tez orada qo'shiladi.</i>"
    )


# ═══════════════════════════════════════════════════════════════════
# 11. STATISTIKA
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text == reply.BTN_STATS)
async def m_stats(message: Message, state: FSMContext):
    await state.clear()
    accounts = await db.get_accounts(message.from_user.id)
    if not accounts:
        await message.answer(
            f"{em.pe('star')} <b>Statistika</b>\n\n"
            f"Hali ma'lumot yo'q. Avval akkaunt qo'shing."
        )
        return
    text = f"{em.pe('star')} <b>Statistika</b>\n\n"
    for a in accounts:
        st = await db.get_stats(a["id"])
        gc = await db.count_groups(a["id"])
        name = a["account_name"] or a["phone"]
        text += (
            f"{em.pe('user')} <b>{name}</b>\n"
            f"   {em.pe('group')} Guruhlar: <b>{gc}</b>\n"
            f"   {em.pe('ok')} Yuborilgan: <b>{st['sent']}</b>\n"
            f"   📅 Bugun: <b>{st['today']}</b>\n"
            f"   ❌ Xato: <b>{st['failed']}</b>\n\n"
        )
    await message.answer(text)


# ═══════════════════════════════════════════════════════════════════
# 12. YORDAM
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text == reply.BTN_HELP)
async def m_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"{em.pe('info')} <b>Yordam</b>\n\n"
        f"{em.pe('rocket')} <b>Bot nima qiladi?</b>\n"
        f"Akkauntingiz nomidan guruhlarga avtomatik xabar yuboradi.\n\n"
        f"<b>Qanday ishlatish:</b>\n"
        f"1. «Profillar» → Akkaunt qo'shing\n"
        f"2. «Guruhlarni sozlash» → Guruhlarni tanlang\n"
        f"3. «Habar matni» → Xabarni yozing\n"
        f"4. «Interval» → Vaqtni belgilang\n"
        f"5. «Autohabar yuborish» → Ishga tushuring\n\n"
        f"❓ Savol: @{config.admin_username}"
    )


# ═══════════════════════════════════════════════════════════════════
# 13. QO'LLANMA
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text == reply.BTN_GUIDE)
async def m_guide(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"{em.pe('book')} <b>Qo'llanma</b>\n\n"
        f"<b>To'liq foydalanish bo'yicha qo'llanma:</b>\n\n"
        f"{em.pe('user')} <b>Akkaunt qo'shish:</b>\n"
        f"«Profillar» → «Akkaunt qo'shish» → QR yoki SMS\n\n"
        f"{em.pe('chat')} <b>Guruhlar:</b>\n"
        f"Akkaunt ulangach guruhlar avtomatik yuklanadi\n\n"
        f"{em.pe('edit')} <b>Xabar:</b>\n"
        f"Har bir akkaunt uchun alohida matn\n\n"
        f"{em.pe('clock')} <b>Interval:</b>\n"
        f"2 daqiqadan to 3 soatgacha\n\n"
        f"<i>Batafsil: @{config.admin_username}</i>"
    )


# ═══════════════════════════════════════════════════════════════════
# 14. AUTOREPLY
# ═══════════════════════════════════════════════════════════════════
@router.message(F.text == reply.BTN_AUTOREPLY)
async def m_autoreply(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"{em.pe('chat')} <b>Autoreply (avto-javob)</b>\n\n"
        f"Siz onlayn bo'lmaganingizda kelgan shaxsiy xabarlarga "
        f"avtomatik javob beradi.\n\n"
        f"<i>Akkauntni «Profillar» dan tanlab, autoreply'ni sozlang.</i>"
    )


# ═══════════════════════════════════════════════════════════════════
# INLINE'DAN ASOSIY MENYUGA QAYTISH
# ═══════════════════════════════════════════════════════════════════
from aiogram.types import CallbackQuery


@router.callback_query(F.data == "back_main")
async def cb_back_main(call: CallbackQuery, state: FSMContext):
    """Inline xabarni o'chirib, ReplyKeyboard asosiy menyuni qaytaradi."""
    await state.clear()
    from app.handlers.start import welcome_text
    user = await db.get_user(call.from_user.id)
    if not user:
        user = await db.get_or_create_user(
            call.from_user.id,
            call.from_user.username or "",
            call.from_user.full_name or "",
        )
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.message.answer(welcome_text(user), reply_markup=reply.main_menu())
    await call.answer()
