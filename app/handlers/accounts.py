"""
Akkaunt ulash handlerlari — QR kod (asosiy) va SMS (muqobil).
"""
import asyncio

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards import menus
from app.raw_api import to_aiogram_markup as _M
from app.keyboards.builder import btn, kb
from app.states import LinkAccount
from app.userbot import login, manager
from app import emoji as em

router = Router(name="accounts")


# ═══════════════════════════════════════════════════════════════════
# AKKAUNTLAR MENYUSI
# ═══════════════════════════════════════════════════════════════════

@router.callback_query(F.data == "__old_accounts_menu")
async def cb_accounts_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await login.cancel_login(call.from_user.id)
    accounts = await db.get_accounts(call.from_user.id)
    text = (
        f"{em.eUS()} <b>Akkauntlar</b>\n\n"
        + (f"Ulangan akkauntlar: <b>{len(accounts)}</b> ta\n\nBoshqarish uchun tanlang:"
           if accounts else
           "Hali akkaunt ulanmagan.\n\n➕ <b>Akkaunt qo'shish</b> tugmasini bosing.")
    )
    await call.message.edit_text(text, reply_markup=_M(menus.accounts_menu(accounts)))
    await call.answer()


@router.callback_query(F.data == "add_account")
async def cb_add_account(call: CallbackQuery, state: FSMContext):
    await state.set_state(LinkAccount.choosing_method)
    text = (
        f"{em.eQR()} <b>Akkaunt ulash</b>\n\n"
        f"Ulash usulini tanlang:\n\n"
        f"📲 <b>QR kod</b> — tezkor, telefon orqali skaner qilasiz\n"
        f"📱 <b>SMS</b> — telefon raqamingizga kod keladi\n\n"
        f"⚠️ <i>Akkauntingiz xavfsiz saqlanadi va faqat siz boshqarasiz.</i>"
    )
    await call.message.edit_text(text, reply_markup=_M(menus.link_method()))
    await call.answer()


# ═══════════════════════════════════════════════════════════════════
# QR ULASH
# ═══════════════════════════════════════════════════════════════════

@router.callback_query(F.data == "link_qr")
async def cb_link_qr(call: CallbackQuery, state: FSMContext):
    await call.answer("QR kod yaratilmoqda...")
    owner_id = call.from_user.id

    try:
        img, qr = await login.start_qr_login(owner_id)
    except Exception as e:
        await call.message.edit_text(
            f"{em.eWN()} QR yaratishda xato:\n<code>{str(e)[:200]}</code>",
            reply_markup=_M(menus.cancel_link_kb()),
        )
        return

    await state.set_state(LinkAccount.qr_waiting)

    caption = (
        f"{em.eQR()} <b>QR kod orqali ulash</b>\n\n"
        f"1️⃣ Telefoningizda <b>Telegram</b>ni oching\n"
        f"2️⃣ <b>Sozlamalar → Qurilmalar</b>\n"
        f"3️⃣ <b>Kompyuterni ulash</b> (Link Desktop Device)\n"
        f"4️⃣ Ushbu QR kodni skaner qiling\n\n"
        f"{em.eCL()} QR <b>60 soniya</b> amal qiladi.\n"
        f"<i>Agar muddati tugasa «🔄 Yangilash» bosing.</i>"
    )

    # Eski xabarni o'chirib, rasm yuboramiz
    try:
        await call.message.delete()
    except Exception:
        pass

    photo = BufferedInputFile(img.read(), filename="qr.png")
    sent = await call.message.answer_photo(
        photo=photo, caption=caption, reply_markup=_M(menus.qr_waiting_kb()),
    )

    # QR natijasini fonda kutamiz
    asyncio.create_task(_watch_qr(call, state, qr, sent.message_id, owner_id))


async def _watch_qr(call: CallbackQuery, state: FSMContext, qr, msg_id: int, owner_id: int):
    """QR skaner natijasini kutadi (fon vazifa)."""
    result = await login.wait_qr_result(owner_id, qr, timeout=60)
    bot = call.bot
    chat_id = call.message.chat.id

    if result["status"] == "ok":
        await _save_account(bot, chat_id, msg_id, state, owner_id, result["account"])

    elif result["status"] == "password":
        await state.set_state(LinkAccount.waiting_password)
        try:
            await bot.edit_message_caption(
                chat_id=chat_id, message_id=msg_id,
                caption=(
                    f"{em.tg_emoji(em.E_KEY, '🔑')} <b>2FA parol kerak</b>\n\n"
                    f"Akkauntingizda ikki bosqichli himoya yoqilgan.\n"
                    f"Parolingizni yuboring:"
                ),
                reply_markup=_M(menus.cancel_link_kb()),
            )
        except Exception:
            await bot.send_message(
                chat_id,
                f"🔑 <b>2FA parol kerak.</b> Parolingizni yuboring:",
                reply_markup=_M(menus.cancel_link_kb()),
            )

    elif result["status"] == "timeout":
        try:
            await bot.edit_message_caption(
                chat_id=chat_id, message_id=msg_id,
                caption=f"{em.eCL()} QR kod muddati tugadi.\n«🔄 Yangilash» bosing.",
                reply_markup=_M(menus.qr_waiting_kb()),
            )
        except Exception:
            pass

    else:  # error
        try:
            await bot.edit_message_caption(
                chat_id=chat_id, message_id=msg_id,
                caption=f"{em.eWN()} Xato:\n<code>{result.get('message', '')}</code>",
                reply_markup=_M(menus.cancel_link_kb()),
            )
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════
# SMS ULASH
# ═══════════════════════════════════════════════════════════════════

@router.callback_query(F.data == "link_sms")
async def cb_link_sms(call: CallbackQuery, state: FSMContext):
    await login.cancel_login(call.from_user.id)
    await state.set_state(LinkAccount.waiting_phone)
    text = (
        f"{em.ePH()} <b>SMS orqali ulash</b>\n\n"
        f"Telefon raqamingizni xalqaro formatda yuboring:\n"
        f"<code>+998901234567</code>\n\n"
        f"{em.eCL()} Raqamingizga Telegram orqali kod keladi."
    )
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.message.answer(text, reply_markup=_M(menus.cancel_link_kb()))
    await call.answer()


@router.message(LinkAccount.waiting_phone)
async def on_phone(message: Message, state: FSMContext):
    phone = message.text.strip().replace(" ", "")
    if not phone.startswith("+") or not phone[1:].isdigit() or len(phone) < 10:
        await message.answer(
            f"{em.eWN()} Raqam noto'g'ri.\nFormat: <code>+998901234567</code>",
            reply_markup=_M(menus.cancel_link_kb()),
        )
        return

    wait = await message.answer(f"{em.eCL()} Kod yuborilmoqda...")
    result = await login.start_sms_login(message.from_user.id, phone)

    if result["status"] == "code_sent":
        await state.update_data(phone=phone)
        await state.set_state(LinkAccount.waiting_code)
        await wait.edit_text(
            f"{em.eOK()} Kod yuborildi!\n\n"
            f"📨 <b>{phone}</b> raqamiga kelgan kodni kiriting.\n\n"
            f"⚠️ <i>Kodni <b>bo'sh joy bilan</b> yozing yoki orasiga belgi qo'ying, "
            f"masalan «1 2 3 4 5» — Telegram avtomatik o'chirib yuborilishidan saqlaydi.</i>",
            reply_markup=_M(menus.cancel_link_kb()),
        )
    else:
        await wait.edit_text(
            f"{em.eWN()} {result.get('message', 'Xato')}",
            reply_markup=_M(menus.cancel_link_kb()),
        )


@router.message(LinkAccount.waiting_code)
async def on_code(message: Message, state: FSMContext):
    # Kod ichidagi bo'shliq/belgilarni tozalaymiz
    code = "".join(c for c in message.text if c.isdigit())
    if not code:
        await message.answer(f"{em.eWN()} Kod faqat raqamlardan iborat bo'lishi kerak.")
        return

    wait = await message.answer(f"{em.eCL()} Tekshirilmoqda...")
    result = await login.submit_sms_code(message.from_user.id, code)
    await _handle_login_result(message, state, wait, result)


# ═══════════════════════════════════════════════════════════════════
# 2FA PAROL (QR/SMS umumiy)
# ═══════════════════════════════════════════════════════════════════

@router.message(LinkAccount.waiting_password)
async def on_password(message: Message, state: FSMContext):
    password = message.text.strip()
    # Parolni o'z ichida saqlamaslik uchun xabarni o'chiramiz
    try:
        await message.delete()
    except Exception:
        pass

    wait = await message.answer(f"{em.eCL()} Parol tekshirilmoqda...")
    result = await login.submit_password(message.from_user.id, password)
    await _handle_login_result(message, state, wait, result)


# ═══════════════════════════════════════════════════════════════════
# NATIJANI QAYTA ISHLASH
# ═══════════════════════════════════════════════════════════════════

async def _handle_login_result(message: Message, state: FSMContext, wait: Message, result: dict):
    if result["status"] == "ok":
        await _save_account(
            message.bot, message.chat.id, wait.message_id, state,
            message.from_user.id, result["account"],
        )
    elif result["status"] == "password":
        await state.set_state(LinkAccount.waiting_password)
        await wait.edit_text(
            f"🔑 <b>2FA parol kerak.</b>\n\nParolingizni yuboring:",
            reply_markup=_M(menus.cancel_link_kb()),
        )
    else:
        await wait.edit_text(
            f"{em.eWN()} {result.get('message', 'Xato')}",
            reply_markup=_M(menus.cancel_link_kb()),
        )


async def _save_account(bot, chat_id: int, msg_id: int, state: FSMContext,
                        owner_id: int, account: dict):
    """Akkauntni DB ga saqlaydi va guruhlarni avtomatik yuklaydi."""
    await state.clear()

    # DB ga saqlash
    row = await db.create_account(
        owner_id=owner_id,
        account_tg_id=account["tg_id"],
        name=account["name"],
        username=account["username"],
        phone=account["phone"],
        session_string=account["session_string"],
    )

    uname = f"@{account['username']}" if account["username"] else account["name"]
    text = (
        f"{em.eOK()} <b>Akkaunt muvaffaqiyatli ulandi!</b>\n\n"
        f"{em.eUS()} Akkaunt: <b>{uname}</b>\n"
        f"📱 Telefon: <code>{account['phone']}</code>\n\n"
        f"{em.eCL()} Guruhlaringiz yuklanmoqda..."
    )
    try:
        await bot.edit_message_caption(chat_id=chat_id, message_id=msg_id, caption=text)
    except Exception:
        try:
            await bot.edit_message_text(text=text, chat_id=chat_id, message_id=msg_id)
        except Exception:
            await bot.send_message(chat_id, text)

    # Guruhlarni avtomatik yuklash
    groups = await manager.fetch_user_groups(account["session_string"])
    added = 0
    for g in groups:
        if await db.add_group(row["id"], g["chat_id"], g["title"]):
            added += 1

    final_text = (
        f"{em.eOK()} <b>Akkaunt ulandi va sozlandi!</b>\n\n"
        f"{em.eUS()} Akkaunt: <b>{uname}</b>\n"
        f"{em.eGR()} Topilgan guruhlar: <b>{added}</b> ta\n\n"
        f"Endi <b>Habar matni</b>ni yozing va <b>Ishga tushuring</b>!"
    )
    from app.keyboards.builder import btn as _btn, inline_kb as _ikb
    final_kb = _M(_ikb([
        [_btn("Bu akkauntni sozlash", cb=f"account_{row['id']}", icon="GEAR", style="primary")],
        [_btn("Yopish", cb="close_msg", icon="BACK", style="danger")],
    ]))
    try:
        await bot.edit_message_caption(
            chat_id=chat_id, message_id=msg_id, caption=final_text, reply_markup=final_kb,
        )
    except Exception:
        await bot.send_message(chat_id, final_text, reply_markup=final_kb)
