"""
Pro tarif to'lovi — karta, stars, va boshqaga sovg'a qilish.

Oqim:
  • pro_card  → karta raqamini ko'rsatadi → "To'ladim" → adminga xabar
  • pro_stars → stars narxini ko'rsatadi → Telegram Stars invoice
  • pro_gift  → kimga sovg'a? → username → to'lov → o'sha odamga Pro

MUHIM: to'lovni HAR DOIM sovg'a qilayotgan odam to'laydi.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, LabeledPrice, PreCheckoutQuery
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards import menus
from app.keyboards.builder import btn, inline_kb
from app.raw_api import send_message, edit_message, answer_callback
from app.states import ProGift
from app import emoji as em
from app.config import config

router = Router(name="pro")


# ═══════════════════════════════════════════════════════════════════
# KARTA ORQALI
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data == "pro_card")
async def cb_pro_card(call: CallbackQuery, state: FSMContext):
    card = await db.get_setting("card_number", "")
    holder = await db.get_setting("card_holder", "")
    price = await db.get_setting("pro_price_card", "50000")
    if not card:
        await answer_callback(call.id, "Karta raqami hali sozlanmagan. Admin bilan bog'laning.", show_alert=True)
        return
    text = (
        f"{em.emoji('CARD')} <b>Karta orqali to'lov</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💳 Karta: <code>{card}</code>\n"
        f"👤 Egasi: <b>{holder}</b>\n"
        f"💰 Summa: <b>{int(price):,} so'm</b>\n\n"
        f"1️⃣ Yuqoridagi kartaga to'lov qiling\n"
        f"2️⃣ «To'ladim» tugmasini bosing\n"
        f"3️⃣ Admin tekshirib Pro beradi\n\n"
        f"<i>Chek rasmini admin so'rashi mumkin.</i>"
    )
    await edit_message(call.message.chat.id, call.message.message_id, text,
                       reply_markup=menus.pro_pay_kb("card"))
    await answer_callback(call.id)


@router.callback_query(F.data == "paid_card")
async def cb_paid_card(call: CallbackQuery):
    user = await db.get_user(call.from_user.id)
    uname = f"@{user['username']}" if user and user["username"] else call.from_user.full_name
    # Adminlarga xabar
    for admin_id in config.admin_ids:
        try:
            await send_message(admin_id,
                f"{em.emoji('CARD')} <b>Yangi to'lov!</b>\n\n"
                f"👤 {uname}\n"
                f"🆔 <code>{call.from_user.id}</code>\n"
                f"💳 Karta orqali to'ladi (tekshiring)\n\n"
                f"Tasdiqlash: Pro berish → <code>{call.from_user.id}</code>",
                reply_markup=inline_kb([
                    [btn("✅ Pro berish", cb=f"admgrant_{call.from_user.id}", icon="OK", style="success")],
                ]))
        except Exception:
            pass
    await edit_message(call.message.chat.id, call.message.message_id,
        f"{em.emoji('OK')} <b>So'rovingiz yuborildi!</b>\n\n"
        f"Admin to'lovni tekshirib, tez orada Pro tarifni faollashtiradi.\n\n"
        f"<i>Odатда 5-30 daqiqa ichida.</i>")
    await answer_callback(call.id, "✅ Yuborildi!", show_alert=True)


# Admin tezkor Pro berish tugmasi
@router.callback_query(F.data.startswith("admgrant_"))
async def cb_admgrant(call: CallbackQuery):
    if not config.is_admin(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True)
        return
    target_id = int(call.data.split("_")[1])
    await db.set_premium(target_id, True)
    await answer_callback(call.id, f"✅ {target_id} ga Pro berildi!", show_alert=True)
    try:
        await send_message(target_id,
            f"{em.emoji('CROWN')} <b>Tabriklaymiz!</b>\n\nPro tarifingiz faollashtirildi! 🎉")
    except Exception:
        pass
    await edit_message(call.message.chat.id, call.message.message_id,
        call.message.text + f"\n\n✅ <b>Pro berildi!</b>" if call.message.text else "✅ Pro berildi!")


# ═══════════════════════════════════════════════════════════════════
# STARS ORQALI (Telegram Stars invoice)
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data == "pro_stars")
async def cb_pro_stars(call: CallbackQuery):
    price = await db.get_setting("pro_price_stars", "500")
    try:
        await call.message.bot.send_invoice(
            chat_id=call.from_user.id,
            title="Pro tarif",
            description="AUTO HABAR PRO — Pro tarif (cheksiz guruh, forward, tugmali xabar)",
            payload=f"pro_self_{call.from_user.id}",
            currency="XTR",  # Telegram Stars
            prices=[LabeledPrice(label="Pro tarif", amount=int(price))],
        )
        await answer_callback(call.id)
    except Exception as e:
        await answer_callback(call.id, f"Xato: {str(e)[:100]}", show_alert=True)


# ═══════════════════════════════════════════════════════════════════
# BOSHQAGA SOVG'A QILISH
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data == "pro_gift")
async def cb_pro_gift(call: CallbackQuery, state: FSMContext):
    await state.set_state(ProGift.waiting_target)
    await edit_message(call.message.chat.id, call.message.message_id,
        f"{em.emoji('GIFT')} <b>Boshqaga Pro sovg'a qilish</b>\n\n"
        f"Kimga sovg'a qilmoqchisiz?\n\n"
        f"Foydalanuvchi <b>username</b> (masalan @user) yoki "
        f"<b>ID</b> raqamini yuboring.\n\n"
        f"💡 <i>To'lovni siz qilasiz, Pro o'sha odamga beriladi.</i>",
        reply_markup=menus.inline_back("pro_back"))
    await answer_callback(call.id)


@router.message(ProGift.waiting_target)
async def on_gift_target(message: Message, state: FSMContext):
    raw = message.text.strip()
    target_user = None

    if raw.startswith("@"):
        # username bo'yicha qidirish
        uname = raw[1:]
        async with db.pool().acquire() as con:
            target_user = await con.fetchrow(
                "SELECT * FROM users WHERE LOWER(username)=LOWER($1)", uname)
        if not target_user:
            await message.answer(
                f"{em.emoji('WARN')} @{uname} botda ro'yxatdan o'tmagan.\n"
                f"U avval /start bosishi kerak. Yoki ID raqamini yuboring.")
            return
    else:
        digits = "".join(c for c in raw if c.isdigit())
        if not digits:
            await message.answer(f"{em.emoji('WARN')} Username (@user) yoki ID yuboring.")
            return
        target_user = await db.get_user(int(digits))
        if not target_user:
            await message.answer(
                f"{em.emoji('WARN')} Bu ID botda yo'q. U avval /start bosishi kerak.")
            return

    price = await db.get_setting("pro_price_stars", "500")
    tname = f"@{target_user['username']}" if target_user["username"] else target_user["full_name"]
    await state.update_data(target_id=target_user["telegram_id"], target_name=tname)
    await state.set_state(ProGift.waiting_payment)

    await message.answer(
        f"{em.emoji('GIFT')} <b>Sovg'a tasdig'i</b>\n\n"
        f"Kimga: <b>{tname}</b>\n"
        f"🆔 <code>{target_user['telegram_id']}</code>\n"
        f"💰 Narx: <b>{price} ⭐️</b>\n\n"
        f"To'lov usulini tanlang:",
        reply_markup=inline_kb([
            [btn("⭐️ Stars bilan to'lash", cb="gift_pay_stars", icon="STAR", style="success")],
            [btn("💳 Karta bilan", cb="gift_pay_card", icon="CARD", style="primary")],
            [btn("Bekor qilish", cb="pro_back", icon="BACK", style="danger")],
        ]))


@router.callback_query(F.data == "gift_pay_stars")
async def cb_gift_stars(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    target_id = data.get("target_id")
    target_name = data.get("target_name", "")
    if not target_id:
        await answer_callback(call.id, "Sessiya tugadi, qaytadan boshlang.", show_alert=True)
        return
    price = await db.get_setting("pro_price_stars", "500")
    try:
        await call.message.bot.send_invoice(
            chat_id=call.from_user.id,
            title=f"Pro sovg'a — {target_name}",
            description=f"{target_name} uchun Pro tarif sovg'asi",
            payload=f"pro_gift_{target_id}",  # kimga berilishi shu yerda
            currency="XTR",
            prices=[LabeledPrice(label="Pro sovg'a", amount=int(price))],
        )
        await answer_callback(call.id)
    except Exception as e:
        await answer_callback(call.id, f"Xato: {str(e)[:100]}", show_alert=True)


@router.callback_query(F.data == "gift_pay_card")
async def cb_gift_card(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    target_id = data.get("target_id")
    target_name = data.get("target_name", "")
    card = await db.get_setting("card_number", "")
    holder = await db.get_setting("card_holder", "")
    price = await db.get_setting("pro_price_card", "50000")
    if not card:
        await answer_callback(call.id, "Karta sozlanmagan.", show_alert=True)
        return
    await edit_message(call.message.chat.id, call.message.message_id,
        f"{em.emoji('GIFT')} <b>Sovg'a uchun to'lov</b>\n\n"
        f"Kimga: <b>{target_name}</b>\n\n"
        f"💳 Karta: <code>{card}</code>\n"
        f"👤 Egasi: <b>{holder}</b>\n"
        f"💰 Summa: <b>{int(price):,} so'm</b>\n\n"
        f"To'lab «To'ladim» bosing — admin tekshirib {target_name} ga Pro beradi.",
        reply_markup=inline_kb([
            [btn("✅ To'ladim", cb=f"giftpaid_{target_id}", icon="OK", style="success")],
            [btn("Bekor", cb="pro_back", icon="BACK", style="danger")],
        ]))
    await answer_callback(call.id)


@router.callback_query(F.data.startswith("giftpaid_"))
async def cb_giftpaid(call: CallbackQuery, state: FSMContext):
    target_id = int(call.data.split("_")[1])
    await state.clear()
    buyer = await db.get_user(call.from_user.id)
    target = await db.get_user(target_id)
    bname = f"@{buyer['username']}" if buyer and buyer["username"] else call.from_user.full_name
    tname = f"@{target['username']}" if target and target["username"] else str(target_id)
    for admin_id in config.admin_ids:
        try:
            await send_message(admin_id,
                f"{em.emoji('GIFT')} <b>Sovg'a to'lovi!</b>\n\n"
                f"To'lovchi: {bname} (<code>{call.from_user.id}</code>)\n"
                f"Kimga: {tname} (<code>{target_id}</code>)\n"
                f"💳 Karta orqali (tekshiring)",
                reply_markup=inline_kb([
                    [btn(f"✅ {tname} ga Pro berish", cb=f"admgrant_{target_id}", icon="OK", style="success")],
                ]))
        except Exception:
            pass
    await edit_message(call.message.chat.id, call.message.message_id,
        f"{em.emoji('OK')} <b>So'rov yuborildi!</b>\n\n"
        f"Admin to'lovni tekshirib, <b>{tname}</b> ga Pro beradi.")
    await answer_callback(call.id, "✅ Yuborildi!", show_alert=True)


@router.callback_query(F.data == "pro_back")
async def cb_pro_back(call: CallbackQuery, state: FSMContext):
    await state.clear()
    user = await db.get_user(call.from_user.id)
    is_prem = user["is_premium"] if user else False
    price_card = await db.get_setting("pro_price_card", "50000")
    price_stars = await db.get_setting("pro_price_stars", "500")
    status = f"{em.emoji('CROWN')} <b>Premium faol</b>" if is_prem else "Oddiy (bepul)"
    text = (
        f"{em.emoji('CROWN')} <b>Pro tarif</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Tarifingiz: {status}\n\n"
        f"💳 Karta: <b>{int(price_card):,} so'm</b>\n"
        f"⭐️ Stars: <b>{price_stars} ⭐</b>\n\n"
        f"{em.emoji('GIFT')} Boshqaga ham sovg'a qila olasiz!"
    )
    await edit_message(call.message.chat.id, call.message.message_id, text,
                       reply_markup=menus.pro_kb(is_prem))
    await answer_callback(call.id)


# ═══════════════════════════════════════════════════════════════════
# TELEGRAM STARS TO'LOVINI QABUL QILISH
# ═══════════════════════════════════════════════════════════════════
@router.pre_checkout_query()
async def pre_checkout(pcq: PreCheckoutQuery):
    await pcq.answer(ok=True)


@router.message(F.successful_payment)
async def on_paid(message: Message):
    payload = message.successful_payment.invoice_payload
    # pro_self_<id> yoki pro_gift_<id>
    parts = payload.split("_")
    target_id = int(parts[-1])
    await db.set_premium(target_id, True)

    if payload.startswith("pro_gift_"):
        # Sovg'a — to'lovchiga va oluvchiga xabar
        await send_message(message.from_user.id,
            f"{em.emoji('OK')} <b>Sovg'a yuborildi!</b>\n\nPro tarif muvaffaqiyatli berildi! 🎁")
        try:
            buyer = await db.get_user(message.from_user.id)
            bname = f"@{buyer['username']}" if buyer and buyer["username"] else "Kimdir"
            await send_message(target_id,
                f"{em.emoji('GIFT')} <b>Sizga sovg'a!</b>\n\n"
                f"{bname} sizga <b>Pro tarif</b> sovg'a qildi! 🎉")
        except Exception:
            pass
    else:
        # O'ziga
        await send_message(message.from_user.id,
            f"{em.emoji('CROWN')} <b>Tabriklaymiz!</b>\n\nPro tarif faollashtirildi! 🎉")
