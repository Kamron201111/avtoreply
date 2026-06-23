"""
Akkaunt ulash — QR (asosiy) + SMS (muqobil) + 2FA. To'liq 3 tilli.
"""
import asyncio

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards import menus
from app.keyboards.builder import btn as _btn, inline_kb as _ikb
from app.raw_api import to_aiogram_markup as _M
from app.states import LinkAccount
from app.userbot import login, manager
from app.i18n import t
from app.lang_util import get_lang
from app import emoji as em

router = Router(name="accounts")


# ═══ AKKAUNT QO'SHISH (Profillar dan "add_account") ═══
@router.callback_query(F.data == "add_account")
async def cb_add(call: CallbackQuery, state: FSMContext):
    lang = await get_lang(call.from_user.id)
    await state.set_state(LinkAccount.choosing_method)
    text = (f"{t('link_title', lang)}\n\n{t('link_choose', lang)}\n\n"
            f"{t('link_qr_info', lang)}\n{t('link_sms_info', lang)}")
    await call.message.edit_text(text, reply_markup=_M(menus.link_method(lang)))
    await call.answer()


# ═══ QR ULASH ═══
@router.callback_query(F.data == "link_qr")
async def cb_qr(call: CallbackQuery, state: FSMContext):
    lang = await get_lang(call.from_user.id)
    await call.answer(t("qr_making", lang))
    owner_id = call.from_user.id
    try:
        img, qr = await login.start_qr_login(owner_id)
    except Exception as e:
        await call.message.edit_text(f"{t('qr_error', lang)}\n<code>{str(e)[:200]}</code>",
                                     reply_markup=_M(menus.cancel_link_kb(lang)))
        return
    await state.set_state(LinkAccount.qr_waiting)
    caption = t("qr_caption", lang)
    try:
        await call.message.delete()
    except Exception:
        pass
    photo = BufferedInputFile(img.read(), filename="qr.png")
    sent = await call.message.answer_photo(photo=photo, caption=caption,
                                           reply_markup=_M(menus.qr_waiting_kb(lang)))
    asyncio.create_task(_watch_qr(call, state, qr, sent.message_id, owner_id, lang))


async def _watch_qr(call, state, qr, msg_id, owner_id, lang):
    result = await login.wait_qr_result(owner_id, qr, timeout=60)
    bot = call.bot
    chat_id = call.message.chat.id
    if result["status"] == "ok":
        await _save_account(bot, chat_id, msg_id, state, owner_id, result["account"], lang)
    elif result["status"] == "password":
        await state.set_state(LinkAccount.waiting_password)
        try:
            await bot.edit_message_caption(chat_id=chat_id, message_id=msg_id,
                                           caption=t("need_2fa_title", lang),
                                           reply_markup=_M(menus.cancel_link_kb(lang)))
        except Exception:
            await bot.send_message(chat_id, t("need_2fa_title", lang),
                                   reply_markup=_M(menus.cancel_link_kb(lang)))
    elif result["status"] == "timeout":
        try:
            await bot.edit_message_caption(chat_id=chat_id, message_id=msg_id,
                                           caption=t("qr_expired", lang),
                                           reply_markup=_M(menus.qr_waiting_kb(lang)))
        except Exception:
            pass
    else:
        try:
            await bot.edit_message_caption(chat_id=chat_id, message_id=msg_id,
                                           caption=f"{t('error_generic', lang)}\n<code>{result.get('message','')}</code>",
                                           reply_markup=_M(menus.cancel_link_kb(lang)))
        except Exception:
            pass


# ═══ SMS ULASH ═══
@router.callback_query(F.data == "link_sms")
async def cb_sms(call: CallbackQuery, state: FSMContext):
    lang = await get_lang(call.from_user.id)
    await login.cancel_login(call.from_user.id)
    await state.set_state(LinkAccount.waiting_phone)
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.message.answer(t("sms_phone", lang), reply_markup=_M(menus.cancel_link_kb(lang)))
    await call.answer()


@router.message(LinkAccount.waiting_phone)
async def on_phone(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    phone = message.text.strip().replace(" ", "")
    if not phone.startswith("+") or not phone[1:].isdigit() or len(phone) < 10:
        await message.answer(t("phone_bad", lang), reply_markup=_M(menus.cancel_link_kb(lang)))
        return
    wait = await message.answer(t("code_sending", lang))
    result = await login.start_sms_login(message.from_user.id, phone)
    if result["status"] == "code_sent":
        await state.update_data(phone=phone)
        await state.set_state(LinkAccount.waiting_code)
        await wait.edit_text(t("code_sent", lang, phone=phone),
                             reply_markup=_M(menus.cancel_link_kb(lang)))
    else:
        await wait.edit_text(f"{t('error_generic', lang)} {result.get('message','')}",
                             reply_markup=_M(menus.cancel_link_kb(lang)))


@router.message(LinkAccount.waiting_code)
async def on_code(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    code = "".join(c for c in message.text if c.isdigit())
    if not code:
        await message.answer(t("code_bad", lang))
        return
    wait = await message.answer(t("checking", lang))
    result = await login.submit_sms_code(message.from_user.id, code)
    await _handle_result(message, state, wait, result, lang)


# ═══ 2FA PAROL ═══
@router.message(LinkAccount.waiting_password)
async def on_password(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    password = message.text.strip()
    try:
        await message.delete()
    except Exception:
        pass
    wait = await message.answer(t("pwd_check", lang))
    result = await login.submit_password(message.from_user.id, password)
    await _handle_result(message, state, wait, result, lang)


async def _handle_result(message, state, wait, result, lang):
    if result["status"] == "ok":
        await _save_account(message.bot, message.chat.id, wait.message_id, state,
                            message.from_user.id, result["account"], lang)
    elif result["status"] == "password":
        await state.set_state(LinkAccount.waiting_password)
        await wait.edit_text(t("need_2fa_title", lang),
                             reply_markup=_M(menus.cancel_link_kb(lang)))
    else:
        await wait.edit_text(f"{t('error_generic', lang)} {result.get('message','')}",
                             reply_markup=_M(menus.cancel_link_kb(lang)))


# ═══ AKKAUNTNI SAQLASH (global UNIQUE tekshiruvi bilan) ═══
async def _save_account(bot, chat_id, msg_id, state, owner_id, account, lang):
    await state.clear()
    # GLOBAL: bu akkaunt allaqachon ulanganmi?
    existing = await db.account_exists(account["tg_id"])
    if existing and existing["owner_id"] != owner_id:
        warn = t("already_linked", lang)
        try:
            await bot.edit_message_caption(chat_id=chat_id, message_id=msg_id, caption=warn)
        except Exception:
            try:
                await bot.edit_message_text(text=warn, chat_id=chat_id, message_id=msg_id)
            except Exception:
                await bot.send_message(chat_id, warn)
        return

    row = await db.create_account(owner_id, account["tg_id"], account["name"],
                                  account["username"], account["phone"], account["session_string"])
    uname = f"@{account['username']}" if account["username"] else account["name"]
    text = t("link_ok", lang, uname=uname, phone=account["phone"])
    try:
        await bot.edit_message_caption(chat_id=chat_id, message_id=msg_id, caption=text)
    except Exception:
        try:
            await bot.edit_message_text(text=text, chat_id=chat_id, message_id=msg_id)
        except Exception:
            await bot.send_message(chat_id, text)

    # Guruhlarni yuklash
    groups = await manager.fetch_user_groups(account["session_string"])
    added = 0
    for g in groups:
        if await db.add_group(row["id"], g["chat_id"], g["title"]):
            added += 1

    final_text = t("link_done", lang, uname=uname, n=added)
    final_kb = _M(_ikb([
        [_btn(t("b_setup_acc", lang), cb=f"account_{row['id']}", icon="GEAR", style="primary")],
        [_btn(t("close", lang), cb="close_msg", icon="BACK", style="danger")],
    ]))
    try:
        await bot.edit_message_caption(chat_id=chat_id, message_id=msg_id,
                                       caption=final_text, reply_markup=final_kb)
    except Exception:
        await bot.send_message(chat_id, final_text, reply_markup=final_kb)
