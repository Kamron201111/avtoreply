"""
Admin panel — katta, 3 tilli, raw API.
Statistika, foydalanuvchilar, premium, narx, karta, qo'llanma, statistika tavsifi,
yordam sozlash, majburiy obuna, murojatlarga javob, broadcast.
"""
import asyncio

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards import menus
from app.keyboards.builder import btn, inline_kb
from app.raw_api import send_message, edit_message, answer_callback
from app.states import AdminStates
from app.i18n import t, TEXTS
from app.lang_util import get_lang
from app import emoji as em
from app.config import config

router = Router(name="admin")


def _adm(uid):
    return config.is_admin(uid)


def _is_btn(text, key):
    if not text:
        return False
    return any(text == v for v in TEXTS.get(key, {}).values())


# ═══ ADMIN PANELNI OCHISH (reply tugmadan) ═══
@router.message(lambda m: _is_btn(m.text, "btn_admin"))
async def open_admin(message: Message, state: FSMContext):
    await state.clear()
    if not _adm(message.from_user.id):
        return
    lang = await get_lang(message.from_user.id)
    await send_message(message.from_user.id, t("adm_title", lang),
                       reply_markup=menus.admin_menu(lang))


@router.callback_query(F.data == "adm_main")
async def cb_main(call: CallbackQuery, state: FSMContext):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    await state.clear()
    lang = await get_lang(call.from_user.id)
    await edit_message(call.message.chat.id, call.message.message_id,
                       t("adm_title", lang), reply_markup=menus.admin_menu(lang))
    await answer_callback(call.id)


# ═══ STATISTIKA ═══
@router.callback_query(F.data == "adm_stats")
async def cb_stats(call: CallbackQuery):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    lang = await get_lang(call.from_user.id)
    st = await db.get_global_stats()
    text = (
        f"{em.emoji('STATS')} <b>Statistika</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        f"{em.emoji('USERS')} Foydalanuvchilar: <b>{st['users']}</b>\n"
        f"{em.emoji('CROWN')} Premium: <b>{st['premium']}</b>\n"
        f"{em.emoji('PHONE')} Profillar: <b>{st['accounts']}</b>\n"
        f"🟢 Faol: <b>{st['active']}</b>\n"
        f"{em.emoji('GROUP')} Guruhlar: <b>{st['groups']}</b>\n"
        f"{em.emoji('OK')} Yuborilgan: <b>{st['sent_total']}</b>"
    )
    await edit_message(call.message.chat.id, call.message.message_id, text,
                       reply_markup=menus.admin_back(lang))
    await answer_callback(call.id)


# ═══ FOYDALANUVCHILAR ═══
@router.callback_query(F.data == "adm_users")
async def cb_users(call: CallbackQuery):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    lang = await get_lang(call.from_user.id)
    users = await db.all_users()
    text = f"{em.emoji('USERS')} Jami <b>{len(users)}</b>:\n\n"
    for u in users[:40]:
        mark = "🚫" if u["is_banned"] else ("👑" if u["is_premium"] else "✅")
        uname = f"@{u['username']}" if u["username"] else u["full_name"]
        text += f"{mark} <code>{u['telegram_id']}</code> {uname}\n"
    if len(users) > 40:
        text += f"\n... +{len(users)-40}"
    await edit_message(call.message.chat.id, call.message.message_id, text,
                       reply_markup=menus.admin_back(lang))
    await answer_callback(call.id)


# ═══ PREMIUM BERISH/OLISH ═══
@router.callback_query(F.data == "adm_give_premium")
async def cb_give(call: CallbackQuery, state: FSMContext):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    lang = await get_lang(call.from_user.id)
    await state.set_state(AdminStates.waiting_premium_id)
    await state.update_data(action="give")
    await edit_message(call.message.chat.id, call.message.message_id,
                       f"{em.emoji('OK')} <b>Premium berish</b>\n\nFoydalanuvchi ID sini yuboring:",
                       reply_markup=menus.admin_back(lang))
    await answer_callback(call.id)


@router.callback_query(F.data == "adm_take_premium")
async def cb_take(call: CallbackQuery, state: FSMContext):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    lang = await get_lang(call.from_user.id)
    await state.set_state(AdminStates.waiting_premium_id)
    await state.update_data(action="take")
    await edit_message(call.message.chat.id, call.message.message_id,
                       f"{em.emoji('WARN')} <b>Premium olish</b>\n\nFoydalanuvchi ID sini yuboring:",
                       reply_markup=menus.admin_back(lang))
    await answer_callback(call.id)


@router.message(AdminStates.waiting_premium_id)
async def on_premium_id(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    lang = await get_lang(message.from_user.id)
    data = await state.get_data()
    give = data.get("action") == "give"
    digits = "".join(c for c in message.text if c.isdigit())
    if not digits:
        await message.answer("❌ ID raqam.")
        return
    tg_id = int(digits)
    if not await db.get_user(tg_id):
        await message.answer("❌ Topilmadi.")
        return
    await db.set_premium(tg_id, give)
    await state.clear()
    await send_message(message.from_user.id,
                       f"{em.emoji('OK')} <code>{tg_id}</code> {'Pro berildi 👑' if give else 'Pro olindi'}!",
                       reply_markup=menus.admin_menu(lang))
    try:
        tlang = await get_lang(tg_id)
        await send_message(tg_id, t("pro_granted", tlang) if give else "Pro tarif tugadi.")
    except Exception:
        pass


# ═══ PRO NARXLARI ═══
@router.callback_query(F.data == "adm_prices")
async def cb_prices(call: CallbackQuery, state: FSMContext):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    lang = await get_lang(call.from_user.id)
    card = await db.get_setting("pro_price_card", "50000")
    stars = await db.get_setting("pro_price_stars", "500")
    await state.set_state(AdminStates.waiting_prices)
    await edit_message(call.message.chat.id, call.message.message_id,
                       f"{em.emoji('MONEY')} <b>Pro narxlari</b>\n\n💳 Karta: <b>{card}</b>\n⭐️ Stars: <b>{stars}</b>\n\n"
                       f"Yangi narx (format: <code>karta stars</code>):\nMasalan: <code>50000 500</code>",
                       reply_markup=menus.admin_back(lang))
    await answer_callback(call.id)


@router.message(AdminStates.waiting_prices)
async def on_prices(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    lang = await get_lang(message.from_user.id)
    parts = message.text.split()
    if len(parts) != 2 or not all(p.isdigit() for p in parts):
        await message.answer("❌ Format: <code>50000 500</code>")
        return
    await db.set_setting("pro_price_card", parts[0])
    await db.set_setting("pro_price_stars", parts[1])
    await state.clear()
    await send_message(message.from_user.id,
                       f"{em.emoji('OK')} Narx yangilandi!\n💳 {int(parts[0]):,}\n⭐️ {parts[1]}",
                       reply_markup=menus.admin_menu(lang))


# ═══ KARTA RAQAMI ═══
@router.callback_query(F.data == "adm_card")
async def cb_card(call: CallbackQuery, state: FSMContext):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    lang = await get_lang(call.from_user.id)
    card = await db.get_setting("card_number", "")
    holder = await db.get_setting("card_holder", "")
    await state.set_state(AdminStates.waiting_card)
    await edit_message(call.message.chat.id, call.message.message_id,
                       f"{em.emoji('CARD')} <b>Karta raqami</b>\n\nJoriy: <code>{card or '-'}</code>\nEgasi: <b>{holder or '-'}</b>\n\n"
                       f"Yangi (format: <code>karta Ism Familiya</code>):\n<code>8600123456789012 Aziz Azizov</code>",
                       reply_markup=menus.admin_back(lang))
    await answer_callback(call.id)


@router.message(AdminStates.waiting_card)
async def on_card(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    lang = await get_lang(message.from_user.id)
    parts = message.text.strip().split(maxsplit=1)
    card_num = "".join(c for c in parts[0] if c.isdigit())
    if len(card_num) < 16:
        await message.answer("❌ 16 raqam.")
        return
    holder = parts[1] if len(parts) > 1 else ""
    await db.set_setting("card_number", card_num)
    await db.set_setting("card_holder", holder)
    await state.clear()
    await send_message(message.from_user.id,
                       f"{em.emoji('OK')} Karta saqlandi!\n💳 <code>{card_num}</code>\n👤 {holder}",
                       reply_markup=menus.admin_menu(lang))


# ═══ QO'LLANMA MATNI ═══
@router.callback_query(F.data == "adm_guide")
async def cb_guide(call: CallbackQuery, state: FSMContext):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    lang = await get_lang(call.from_user.id)
    cur = await db.get_setting("guide_uz", "")
    await state.set_state(AdminStates.waiting_guide)
    await edit_message(call.message.chat.id, call.message.message_id,
                       f"{em.emoji('BOOK')} <b>Qo'llanma matni</b>\n\nJoriy:\n<blockquote>{cur[:300] or '(yoq)'}</blockquote>\n\n"
                       f"Yangi qo'llanma matnini yuboring (HTML mumkin):",
                       reply_markup=menus.admin_back(lang))
    await answer_callback(call.id)


@router.message(AdminStates.waiting_guide)
async def on_guide(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    lang = await get_lang(message.from_user.id)
    text = message.html_text or message.text or ""
    await db.set_setting("guide_uz", text)
    await db.set_setting("guide_ru", text)
    await db.set_setting("guide_en", text)
    await state.clear()
    await send_message(message.from_user.id, f"{em.emoji('OK')} Qo'llanma saqlandi!",
                       reply_markup=menus.admin_menu(lang))


# ═══ STATISTIKA TAVSIFI ═══
@router.callback_query(F.data == "adm_statsdesc")
async def cb_statsdesc(call: CallbackQuery, state: FSMContext):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    lang = await get_lang(call.from_user.id)
    cur = await db.get_setting("stats_desc_uz", "")
    await state.set_state(AdminStates.waiting_statsdesc)
    await edit_message(call.message.chat.id, call.message.message_id,
                       f"{em.emoji('STATS')} <b>Statistika tavsifi</b>\n\nJoriy:\n<blockquote>{cur[:300] or '(yoq)'}</blockquote>\n\n"
                       f"Statistika bo'limida ko'rinadigan tavsifni yuboring:",
                       reply_markup=menus.admin_back(lang))
    await answer_callback(call.id)


@router.message(AdminStates.waiting_statsdesc)
async def on_statsdesc(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    lang = await get_lang(message.from_user.id)
    text = message.html_text or message.text or ""
    await db.set_setting("stats_desc_uz", text)
    await db.set_setting("stats_desc_ru", text)
    await db.set_setting("stats_desc_en", text)
    await state.clear()
    await send_message(message.from_user.id, f"{em.emoji('OK')} Saqlandi!",
                       reply_markup=menus.admin_menu(lang))


# ═══ YORDAM SOZLASH (kanal/chat/admin) ═══
@router.callback_query(F.data == "adm_help")
async def cb_help(call: CallbackQuery, state: FSMContext):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    lang = await get_lang(call.from_user.id)
    ch = await db.get_setting("help_channel", "")
    chat = await db.get_setting("help_chat", "")
    adm = await db.get_setting("help_admin", "")
    await state.set_state(AdminStates.waiting_help)
    await edit_message(call.message.chat.id, call.message.message_id,
                       f"{em.emoji('INFO')} <b>Yordam sozlash</b>\n\nKanal: {ch or '-'}\nChat: {chat or '-'}\nAdmin: {adm or '-'}\n\n"
                       f"Yangi (format: <code>@kanal @chat @admin</code>):",
                       reply_markup=menus.admin_back(lang))
    await answer_callback(call.id)


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
    await send_message(message.from_user.id, f"{em.emoji('OK')} Yordam sozlandi!",
                       reply_markup=menus.admin_menu(lang))


# ═══ MAJBURIY OBUNA ═══
@router.callback_query(F.data == "adm_channels")
async def cb_channels(call: CallbackQuery, state: FSMContext):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    lang = await get_lang(call.from_user.id)
    channels = await db.get_channels()
    text = f"{em.emoji('CHAT')} <b>Majburiy obuna kanallari</b>\n\n"
    rows = []
    if channels:
        for c in channels:
            text += f"• {c['title']} ({c['channel_id']})\n"
            rows.append([btn(f"🗑 {c['title']}", cb=f"chdel_{c['id']}", style="danger")])
    else:
        text += "(yo'q)\n"
    text += "\nYangi kanal qo'shish uchun tugma:"
    rows.append([btn("➕ Kanal qo'shish", cb="chadd", icon="OK", style="success")])
    rows.append([btn(t("back", lang), cb="adm_main", icon="BACK", style="danger")])
    await edit_message(call.message.chat.id, call.message.message_id, text,
                       reply_markup=inline_kb(rows))
    await answer_callback(call.id)


@router.callback_query(F.data == "chadd")
async def cb_chadd(call: CallbackQuery, state: FSMContext):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    lang = await get_lang(call.from_user.id)
    await state.set_state(AdminStates.waiting_channel)
    await edit_message(call.message.chat.id, call.message.message_id,
                       f"{em.emoji('CHAT')} Kanal qo'shish\n\nFormat: <code>@kanal Kanal nomi</code>\n"
                       f"yoki ID bilan: <code>-1001234567 Nomi</code>",
                       reply_markup=menus.admin_back(lang))
    await answer_callback(call.id)


@router.message(AdminStates.waiting_channel)
async def on_channel(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    lang = await get_lang(message.from_user.id)
    parts = message.text.strip().split(maxsplit=1)
    ch_id = parts[0]
    title = parts[1] if len(parts) > 1 else ch_id
    invite = f"https://t.me/{ch_id.lstrip('@')}" if ch_id.startswith("@") else ""
    await db.add_channel(ch_id, title, invite)
    await state.clear()
    await send_message(message.from_user.id, f"{em.emoji('OK')} Kanal qo'shildi: {title}",
                       reply_markup=menus.admin_menu(lang))


@router.callback_query(F.data.startswith("chdel_"))
async def cb_chdel(call: CallbackQuery):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    ch_id = int(call.data.split("_")[1])
    await db.remove_channel(ch_id)
    await answer_callback(call.id, "🗑 O'chirildi", show_alert=True)
    await cb_channels(call, None)


# ═══ MUROJATGA JAVOB (ikki tomonlama) ═══
@router.callback_query(F.data.startswith("ticket_reply_"))
async def cb_ticket_reply(call: CallbackQuery, state: FSMContext):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    user_id = int(call.data.split("_")[2])
    await state.set_state(AdminStates.waiting_ticket_reply)
    await state.update_data(ticket_user=user_id)
    await send_message(call.from_user.id,
                       f"✍️ <code>{user_id}</code> ga javobingizni yozing:")
    await answer_callback(call.id)


@router.message(AdminStates.waiting_ticket_reply)
async def on_ticket_reply(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    data = await state.get_data()
    user_id = data.get("ticket_user")
    await state.clear()
    if not user_id:
        return
    tlang = await get_lang(user_id)
    reply_text = message.html_text or message.text or ""
    try:
        await send_message(user_id,
                           f"{em.emoji('REPLY')} <b>Admin javobi:</b>\n\n{reply_text}")
        await send_message(message.from_user.id, f"{em.emoji('OK')} Javob yuborildi!")
    except Exception:
        await send_message(message.from_user.id, "❌ Yuborilmadi (user botni bloklagan?).")


# ═══ MUROJATLAR RO'YXATI ═══
@router.callback_query(F.data == "adm_tickets")
async def cb_tickets(call: CallbackQuery):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    lang = await get_lang(call.from_user.id)
    async with db.pool().acquire() as con:
        tickets = await con.fetch("SELECT * FROM tickets WHERE status='open' ORDER BY id DESC LIMIT 10")
    if not tickets:
        text = f"{em.emoji('REPLY')} <b>Murojatlar</b>\n\nYangi murojat yo'q."
        await edit_message(call.message.chat.id, call.message.message_id, text,
                           reply_markup=menus.admin_back(lang))
        await answer_callback(call.id)
        return
    text = f"{em.emoji('REPLY')} <b>Ochiq murojatlar:</b>\n\n"
    rows = []
    for tk in tickets:
        text += f"#{tk['id']} {tk['username']}: {tk['message'][:50]}\n\n"
        rows.append([btn(f"✍️ #{tk['id']} javob", cb=f"ticket_reply_{tk['user_id']}", style="success")])
    rows.append([btn(t("back", lang), cb="adm_main", icon="BACK", style="danger")])
    await edit_message(call.message.chat.id, call.message.message_id, text,
                       reply_markup=inline_kb(rows))
    await answer_callback(call.id)


# ═══ BROADCAST ═══
@router.callback_query(F.data == "adm_broadcast")
async def cb_broadcast(call: CallbackQuery, state: FSMContext):
    if not _adm(call.from_user.id):
        await answer_callback(call.id, "❌", show_alert=True); return
    lang = await get_lang(call.from_user.id)
    await state.set_state(AdminStates.waiting_broadcast)
    await edit_message(call.message.chat.id, call.message.message_id,
                       f"{em.emoji('ROCKET')} <b>Broadcast</b>\n\nBarchaga yuboriladigan xabarni yuboring:",
                       reply_markup=menus.admin_back(lang))
    await answer_callback(call.id)


@router.message(AdminStates.waiting_broadcast)
async def on_broadcast(message: Message, state: FSMContext):
    if not _adm(message.from_user.id):
        return
    lang = await get_lang(message.from_user.id)
    await state.clear()
    users = await db.all_users()
    targets = [u for u in users if not u["is_banned"]]
    prog = await message.answer(f"{em.emoji('ROCKET')} 0/{len(targets)}")
    sent = failed = 0
    for u in targets:
        try:
            await message.copy_to(chat_id=u["telegram_id"])
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)
    await prog.edit_text(f"{em.emoji('OK')} Yuborildi: {sent}\n❌ Xato: {failed}")
