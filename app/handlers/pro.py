"""
Pro tarif — karta, stars, sovg'a, murojat. 3 tilli.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, LabeledPrice, PreCheckoutQuery
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards import menus
from app.keyboards.builder import btn, inline_kb
from app.raw_api import send_message, edit_message, answer_callback
from app.states import ProGift, Support
from app.i18n import t
from app.lang_util import get_lang
from app import emoji as em
from app.config import config

router = Router(name="pro")


def _som(lang):
    return "so'm" if lang == "uz" else "сум" if lang == "ru" else "UZS"


# ═══ KARTA ═══
@router.callback_query(F.data == "pro_card")
async def cb_pro_card(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    card = await db.get_setting("card_number", "")
    holder = await db.get_setting("card_holder", "")
    price = await db.get_setting("pro_price_card", "50000")
    if not card:
        await answer_callback(call.id, t("no_card", lang), show_alert=True)
        return
    text = t("pro_card_info", lang, card=card, holder=holder,
             price=f"{int(price):,} {_som(lang)}")
    await edit_message(call.message.chat.id, call.message.message_id, text,
                       reply_markup=menus.pro_pay_kb("card", lang))
    await answer_callback(call.id)


@router.callback_query(F.data == "paid_card")
async def cb_paid_card(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    user = await db.get_user(call.from_user.id)
    uname = f"@{user['username']}" if user and user["username"] else call.from_user.full_name
    for admin_id in config.admin_ids:
        try:
            await send_message(admin_id,
                f"{em.emoji('CARD')} <b>Yangi to'lov!</b>\n\n👤 {uname}\n🆔 <code>{call.from_user.id}</code>\n💳 Karta orqali (tekshiring)",
                reply_markup=inline_kb([[btn("✅ Pro berish", cb=f"admgrant_{call.from_user.id}", icon="OK", style="success")]]))
        except Exception:
            pass
    await edit_message(call.message.chat.id, call.message.message_id, t("paid_sent", lang))
    await answer_callback(call.id, "✅", show_alert=True)


@router.callback_query(F.data.startswith("admgrant_"))
async def cb_admgrant(call: CallbackQuery):
    if not config.is_admin(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True)
        return
    target_id = int(call.data.split("_")[1])
    await db.set_premium(target_id, True)
    await answer_callback(call.id, f"✅ {target_id} Pro!", show_alert=True)
    tlang = await get_lang(target_id)
    try:
        await send_message(target_id, t("pro_granted", tlang))
    except Exception:
        pass


# ═══ STARS ═══
@router.callback_query(F.data == "pro_stars")
async def cb_pro_stars(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    price = await db.get_setting("pro_price_stars", "500")
    try:
        await call.message.bot.send_invoice(
            chat_id=call.from_user.id, title="Pro", description="AUTO HABAR PRO — Pro tarif",
            payload=f"pro_self_{call.from_user.id}", currency="XTR",
            prices=[LabeledPrice(label="Pro", amount=int(price))])
        await answer_callback(call.id)
    except Exception as e:
        await answer_callback(call.id, str(e)[:90], show_alert=True)


# ═══ SOVG'A ═══
@router.callback_query(F.data == "pro_gift")
async def cb_pro_gift(call: CallbackQuery, state: FSMContext):
    lang = await get_lang(call.from_user.id)
    await state.set_state(ProGift.waiting_target)
    await edit_message(call.message.chat.id, call.message.message_id,
                       f"{t('gift_title', lang)}\n\n{t('gift_who', lang)}",
                       reply_markup=menus.inline_back("pro_back", lang))
    await answer_callback(call.id)


@router.message(ProGift.waiting_target)
async def on_gift_target(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    raw = message.text.strip()
    target = None
    if raw.startswith("@"):
        async with db.pool().acquire() as con:
            target = await con.fetchrow("SELECT * FROM users WHERE LOWER(username)=LOWER($1)", raw[1:])
    else:
        digits = "".join(c for c in raw if c.isdigit())
        if digits:
            target = await db.get_user(int(digits))
    if not target:
        await message.answer(t("gift_notfound", lang))
        return
    price = await db.get_setting("pro_price_stars", "500")
    tname = f"@{target['username']}" if target["username"] else target["full_name"]
    await state.update_data(target_id=target["telegram_id"], target_name=tname)
    await state.set_state(ProGift.waiting_payment)
    await message.answer(
        t("gift_confirm", lang, name=tname, id=target["telegram_id"], price=f"{price} ⭐️"),
        reply_markup=inline_kb([
            [btn(t("b_pro_stars", lang), cb="gift_pay_stars", icon="STAR", style="success")],
            [btn(t("b_pro_card", lang), cb="gift_pay_card", icon="CARD", style="primary")],
            [btn(t("cancel", lang), cb="pro_back", icon="BACK", style="danger")],
        ]))


@router.callback_query(F.data == "gift_pay_stars")
async def cb_gift_stars(call: CallbackQuery, state: FSMContext):
    lang = await get_lang(call.from_user.id)
    data = await state.get_data()
    target_id = data.get("target_id")
    target_name = data.get("target_name", "")
    if not target_id:
        await answer_callback(call.id, "?", show_alert=True)
        return
    price = await db.get_setting("pro_price_stars", "500")
    try:
        await call.message.bot.send_invoice(
            chat_id=call.from_user.id, title=f"Pro → {target_name}",
            description=f"{target_name}", payload=f"pro_gift_{target_id}",
            currency="XTR", prices=[LabeledPrice(label="Pro gift", amount=int(price))])
        await answer_callback(call.id)
    except Exception as e:
        await answer_callback(call.id, str(e)[:90], show_alert=True)


@router.callback_query(F.data == "gift_pay_card")
async def cb_gift_card(call: CallbackQuery, state: FSMContext):
    lang = await get_lang(call.from_user.id)
    data = await state.get_data()
    target_id = data.get("target_id")
    target_name = data.get("target_name", "")
    card = await db.get_setting("card_number", "")
    holder = await db.get_setting("card_holder", "")
    price = await db.get_setting("pro_price_card", "50000")
    if not card:
        await answer_callback(call.id, t("no_card", lang), show_alert=True)
        return
    text = (f"{t('gift_title', lang)} — {target_name}\n\n"
            f"💳 <code>{card}</code>\n👤 {holder}\n💰 {int(price):,} {_som(lang)}")
    await edit_message(call.message.chat.id, call.message.message_id, text,
                       reply_markup=inline_kb([
                           [btn(t("b_paid", lang), cb=f"giftpaid_{target_id}", icon="OK", style="success")],
                           [btn(t("cancel", lang), cb="pro_back", icon="BACK", style="danger")],
                       ]))
    await answer_callback(call.id)


@router.callback_query(F.data.startswith("giftpaid_"))
async def cb_giftpaid(call: CallbackQuery, state: FSMContext):
    lang = await get_lang(call.from_user.id)
    target_id = int(call.data.split("_")[1])
    await state.clear()
    buyer = await db.get_user(call.from_user.id)
    target = await db.get_user(target_id)
    bname = f"@{buyer['username']}" if buyer and buyer["username"] else call.from_user.full_name
    tname = f"@{target['username']}" if target and target["username"] else str(target_id)
    for admin_id in config.admin_ids:
        try:
            await send_message(admin_id,
                f"{em.emoji('GIFT')} <b>Sovg'a to'lovi!</b>\n\nTo'lovchi: {bname} (<code>{call.from_user.id}</code>)\nKimga: {tname} (<code>{target_id}</code>)\n💳 Karta (tekshiring)",
                reply_markup=inline_kb([[btn(f"✅ {tname} Pro", cb=f"admgrant_{target_id}", icon="OK", style="success")]]))
        except Exception:
            pass
    await edit_message(call.message.chat.id, call.message.message_id, t("paid_sent", lang))
    await answer_callback(call.id, "✅", show_alert=True)


@router.callback_query(F.data == "pro_back")
async def cb_pro_back(call: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = await get_lang(call.from_user.id)
    user = await db.get_user(call.from_user.id)
    is_prem = user["is_premium"] if user else False
    pc = await db.get_setting("pro_price_card", "50000")
    ps = await db.get_setting("pro_price_stars", "500")
    status = t("pro_active", lang) if is_prem else t("pro_free", lang)
    text = (f"{t('pro_title', lang)}\n━━━━━━━━━━━━━━━━━━━━\n{t('pro_your', lang)}: {status}\n\n"
            f"💳 {int(pc):,} {_som(lang)}\n⭐️ {ps} ⭐\n\n{t('pro_gift_hint', lang)}")
    await edit_message(call.message.chat.id, call.message.message_id, text,
                       reply_markup=menus.pro_kb(is_prem, lang))
    await answer_callback(call.id)


# ═══ STARS TO'LOVNI QABUL ═══
@router.pre_checkout_query()
async def pre_checkout(pcq: PreCheckoutQuery):
    await pcq.answer(ok=True)


@router.message(F.successful_payment)
async def on_paid(message: Message):
    payload = message.successful_payment.invoice_payload
    target_id = int(payload.split("_")[-1])
    await db.set_premium(target_id, True)
    lang = await get_lang(message.from_user.id)
    if payload.startswith("pro_gift_"):
        await send_message(message.from_user.id, t("gift_sent", lang))
        try:
            buyer = await db.get_user(message.from_user.id)
            bname = f"@{buyer['username']}" if buyer and buyer["username"] else "Kimdir"
            tlang = await get_lang(target_id)
            await send_message(target_id, t("gift_received", tlang, name=bname))
        except Exception:
            pass
    else:
        await send_message(message.from_user.id, t("pro_granted", lang))


# ═══════════════════════════════════════════════════════════════════
# MUROJAT (foydalanuvchi -> admin, ikki tomonlama)
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data == "contact_admin")
async def cb_contact(call: CallbackQuery, state: FSMContext):
    lang = await get_lang(call.from_user.id)
    await state.set_state(Support.waiting_message)
    await edit_message(call.message.chat.id, call.message.message_id,
                       t("contact_q", lang), reply_markup=menus.close_kb(lang))
    await answer_callback(call.id)


@router.message(Support.waiting_message)
async def on_contact_msg(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    await state.clear()
    user = await db.get_user(message.from_user.id)
    uname = f"@{user['username']}" if user and user["username"] else message.from_user.full_name
    ticket = await db.create_ticket(message.from_user.id, uname, message.text or "(media)")
    # Adminlarga "Javob berish" tugmasi bilan
    for admin_id in config.admin_ids:
        try:
            await send_message(admin_id,
                f"{em.emoji('REPLY')} <b>Yangi murojat #{ticket['id']}</b>\n\n"
                f"👤 {uname} (<code>{message.from_user.id}</code>)\n\n"
                f"💬 {message.text or '(media)'}",
                reply_markup=inline_kb([[btn("✍️ Javob berish", cb=f"ticket_reply_{message.from_user.id}", icon="EDIT", style="success")]]))
        except Exception:
            pass
    await send_message(message.from_user.id, t("contact_sent", lang))
