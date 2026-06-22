"""
Akkaunt (profil) boshqaruvi — raw API bilan.
Callbacklar: account_, start_, stop_, setint_, gtog_, grp_*, reply_*, mtype_*, acc_*
"""
from datetime import datetime, timedelta, timezone

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards import menus
from app.raw_api import send_message, edit_message, answer_callback, delete_message
from app.states import MessageSetup, AutoReplySetup
from app.userbot import manager
from app import emoji as em
from app.config import config

router = Router(name="manage")


async def _panel_text(account) -> str:
    """Boshqaruv panel matni (menu.py bilan bir xil)."""
    from app.handlers.menu import account_panel_text
    return await account_panel_text(account)


async def _check(call, account_id):
    """Akkaunt egasini tekshiradi."""
    account = await db.get_account(account_id)
    if not account or account["owner_id"] != call.from_user.id:
        await answer_callback(call.id, "❌ Topilmadi", show_alert=True)
        return None
    return account


# ═══════════════════════════════════════════════════════════════════
# AKKAUNT PANELINI OCHISH
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data.startswith("account_"))
async def cb_account(call: CallbackQuery, state: FSMContext):
    await state.clear()
    account_id = int(call.data.split("_")[1])
    account = await _check(call, account_id)
    if not account:
        return
    s = await db.get_autosend(account_id)
    await edit_message(
        call.message.chat.id, call.message.message_id,
        await _panel_text(account),
        reply_markup=menus.account_panel(account_id, s["is_running"], s["mention_enabled"]),
    )
    await answer_callback(call.id)


# ═══════════════════════════════════════════════════════════════════
# START / STOP
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data.startswith("start_"))
async def cb_start(call: CallbackQuery):
    account_id = int(call.data.split("_")[1])
    account = await _check(call, account_id)
    if not account:
        return
    s = await db.get_autosend(account_id)
    if not s["message_text"]:
        await answer_callback(call.id, "❌ Avval «Habar matni» ni sozlang!", show_alert=True)
        return
    if not await db.get_enabled_groups(account_id):
        await answer_callback(call.id, "❌ Avval «Guruhlarni sozlash» dan guruh tanlang!", show_alert=True)
        return
    nxt = datetime.now(timezone.utc) + timedelta(minutes=s["interval_min"])
    await db.set_running(account_id, True, nxt)
    await answer_callback(call.id, "🟢 Ishga tushdi!", show_alert=True)
    account = await db.get_account(account_id)
    await edit_message(call.message.chat.id, call.message.message_id,
                       await _panel_text(account),
                       reply_markup=menus.account_panel(account_id, True, s["mention_enabled"]))


@router.callback_query(F.data.startswith("stop_"))
async def cb_stop(call: CallbackQuery):
    account_id = int(call.data.split("_")[1])
    account = await _check(call, account_id)
    if not account:
        return
    await db.set_running(account_id, False)
    await answer_callback(call.id, "🔴 To'xtatildi", show_alert=True)
    s = await db.get_autosend(account_id)
    account = await db.get_account(account_id)
    await edit_message(call.message.chat.id, call.message.message_id,
                       await _panel_text(account),
                       reply_markup=menus.account_panel(account_id, False, s["mention_enabled"]))


# ═══════════════════════════════════════════════════════════════════
# MENTION TOGGLE
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data.startswith("acc_mention_"))
async def cb_mention(call: CallbackQuery):
    account_id = int(call.data.split("_")[2])
    account = await _check(call, account_id)
    if not account:
        return
    s = await db.get_autosend(account_id)
    new_val = not s["mention_enabled"]
    await db.update_autosend(account_id, mention_enabled=new_val)
    _mtxt = "yoqildi" if new_val else "o'chirildi"
    await answer_callback(call.id, f"Mention {_mtxt}")
    account = await db.get_account(account_id)
    await edit_message(call.message.chat.id, call.message.message_id,
                       await _panel_text(account),
                       reply_markup=menus.account_panel(account_id, s["is_running"], new_val))


# ═══════════════════════════════════════════════════════════════════
# AVTO-O'CHIRISH TAYMERI
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data.startswith("acc_timer_"))
async def cb_timer(call: CallbackQuery):
    account_id = int(call.data.split("_")[2])
    account = await _check(call, account_id)
    if not account:
        return
    await answer_callback(call.id,
        "Avto-o'chirish: yuborilgan xabar belgilangan vaqtdan keyin o'chadi. "
        "Tez orada to'liq sozlanadi.", show_alert=True)


# ═══════════════════════════════════════════════════════════════════
# AKKAUNTNI O'CHIRISH
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data.startswith("del_acc_"))
async def cb_del(call: CallbackQuery):
    account_id = int(call.data.split("_")[2])
    account = await _check(call, account_id)
    if not account:
        return
    await manager.disconnect_client(account_id)
    await db.delete_account(account_id)
    await answer_callback(call.id, "🗑 Profil o'chirildi", show_alert=True)
    accounts = await db.get_accounts(call.from_user.id)
    await edit_message(call.message.chat.id, call.message.message_id,
                       f"{em.emoji('USERS')} <b>Profillar</b>\n\nUlangan: <b>{len(accounts)}</b> ta",
                       reply_markup=menus.accounts_menu(accounts))


# ═══════════════════════════════════════════════════════════════════
# HABAR TURI (Image 2) — mtype_*
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data.startswith("mtype_text_"))
async def cb_mtype_text(call: CallbackQuery, state: FSMContext):
    account_id = int(call.data.split("_")[2])
    if not await _check(call, account_id):
        return
    await db.update_autosend(account_id, message_type="text")
    await state.set_state(MessageSetup.waiting_text)
    await state.update_data(account_id=account_id)
    await edit_message(call.message.chat.id, call.message.message_id,
        f"{em.emoji('EDIT')} <b>Matnli xabar</b>\n\n"
        f"Guruhlarga yuboriladigan matnni yuboring.\n\n"
        f"💡 <i>HTML: <b>qalin</b>, <i>kursiv</i>, havola ishlaydi.</i>",
        reply_markup=menus.inline_back(f"account_{account_id}"))
    await answer_callback(call.id)


@router.callback_query(F.data.startswith("mtype_photo_"))
async def cb_mtype_photo(call: CallbackQuery, state: FSMContext):
    account_id = int(call.data.split("_")[2])
    if not await _check(call, account_id):
        return
    await db.update_autosend(account_id, message_type="photo")
    await state.set_state(MessageSetup.waiting_text)
    await state.update_data(account_id=account_id, want_photo=True)
    await edit_message(call.message.chat.id, call.message.message_id,
        f"{em.emoji('USER')} <b>Rasm+matn</b>\n\n"
        f"Rasmni izoh (caption) bilan yuboring.",
        reply_markup=menus.inline_back(f"account_{account_id}"))
    await answer_callback(call.id)


@router.callback_query(F.data.startswith("mtype_btn_"))
async def cb_mtype_btn(call: CallbackQuery, state: FSMContext):
    account_id = int(call.data.split("_")[2])
    if not await _check(call, account_id):
        return
    await answer_callback(call.id,
        "Tugmali xabar: matn + inline tugma. Tez orada to'liq sozlanadi.", show_alert=True)


@router.callback_query(F.data.startswith("mtype_fwd_"))
@router.callback_query(F.data.startswith("mtype_multi_"))
async def cb_mtype_locked(call: CallbackQuery):
    user = await db.get_user(call.from_user.id)
    if not (user and user["is_premium"]):
        await answer_callback(call.id, "🔒 Bu funksiya faqat Pro tarifda!", show_alert=True)
        return
    await answer_callback(call.id, "Tez orada qo'shiladi.", show_alert=True)


# ═══════════════════════════════════════════════════════════════════
# HABAR MATNINI QABUL QILISH
# ═══════════════════════════════════════════════════════════════════
@router.message(MessageSetup.waiting_text)
async def on_msg_text(message: Message, state: FSMContext):
    data = await state.get_data()
    account_id = data["account_id"]
    want_photo = data.get("want_photo", False)

    file_id = ""
    if want_photo:
        if not message.photo:
            await message.answer(f"{em.emoji('WARN')} Iltimos rasm yuboring (izoh bilan).")
            return
        file_id = message.photo[-1].file_id
        text = message.html_text or message.caption or ""
    else:
        text = message.html_text or message.text or ""

    if not text.strip() and not file_id:
        await message.answer(f"{em.emoji('WARN')} Matn bo'sh bo'lmasin.")
        return

    await db.update_autosend(account_id, message_text=text, message_file_id=file_id)
    await state.clear()
    account = await db.get_account(account_id)
    s = await db.get_autosend(account_id)
    await send_message(message.from_user.id,
        f"{em.emoji('OK')} <b>Xabar saqlandi!</b>\n\n<blockquote>{text[:300]}</blockquote>",
        reply_markup=menus.account_panel(account_id, s["is_running"], s["mention_enabled"]))


# ═══════════════════════════════════════════════════════════════════
# INTERVAL — setint_, int_manual_
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data.startswith("setint_"))
async def cb_setint(call: CallbackQuery):
    _, account_id, minutes = call.data.split("_")
    account_id, minutes = int(account_id), int(minutes)
    if not await _check(call, account_id):
        return
    user = await db.get_user(call.from_user.id)
    if not user["is_premium"] and minutes < config.free_min_interval:
        await answer_callback(call.id,
            f"⚠️ Bepul tarifda minimal {config.free_min_interval} daqiqa. Pro oling!",
            show_alert=True)
        return
    await db.update_autosend(account_id, interval_min=minutes)
    await answer_callback(call.id, f"✅ {minutes} daqiqa")
    s = await db.get_autosend(account_id)
    await edit_message(call.message.chat.id, call.message.message_id,
        f"{em.emoji('TIMER')} <b>Habar oralig'i</b>\n\nJoriy interval: <b>{minutes} daqiqa</b>\n\nKerakli vaqtni tanlang:",
        reply_markup=menus.interval_kb(account_id, minutes))


@router.callback_query(F.data.startswith("int_manual_"))
async def cb_int_manual(call: CallbackQuery, state: FSMContext):
    account_id = int(call.data.split("_")[2])
    if not await _check(call, account_id):
        return
    await state.set_state(MessageSetup.waiting_interval)
    await state.update_data(account_id=account_id)
    await edit_message(call.message.chat.id, call.message.message_id,
        f"{em.emoji('EDIT')} <b>Qo'lda interval</b>\n\nDaqiqalarda son kiriting (masalan 25):",
        reply_markup=menus.inline_back(f"acc_int_back_{account_id}"))
    await answer_callback(call.id)


@router.message(MessageSetup.waiting_interval)
async def on_int_manual(message: Message, state: FSMContext):
    data = await state.get_data()
    account_id = data["account_id"]
    digits = "".join(c for c in message.text if c.isdigit())
    if not digits:
        await message.answer(f"{em.emoji('WARN')} Faqat son kiriting.")
        return
    minutes = int(digits)
    if minutes < 1 or minutes > 1440:
        await message.answer(f"{em.emoji('WARN')} 1 — 1440 daqiqa oralig'ida bo'lsin.")
        return
    user = await db.get_user(message.from_user.id)
    if not user["is_premium"] and minutes < config.free_min_interval:
        await message.answer(f"⚠️ Bepul tarifda minimal {config.free_min_interval} daqiqa.")
        return
    await db.update_autosend(account_id, interval_min=minutes)
    await state.clear()
    s = await db.get_autosend(account_id)
    account = await db.get_account(account_id)
    await send_message(message.from_user.id,
        f"{em.emoji('OK')} Interval <b>{minutes} daqiqa</b> o'rnatildi!",
        reply_markup=menus.account_panel(account_id, s["is_running"], s["mention_enabled"]))


@router.callback_query(F.data.startswith("acc_int_back_"))
async def cb_int_back(call: CallbackQuery, state: FSMContext):
    await state.clear()
    account_id = int(call.data.split("_")[3])
    s = await db.get_autosend(account_id)
    await edit_message(call.message.chat.id, call.message.message_id,
        f"{em.emoji('TIMER')} <b>Habar oralig'i</b>\n\nJoriy interval: <b>{s['interval_min']} daqiqa</b>\n\nKerakli vaqtni tanlang:",
        reply_markup=menus.interval_kb(account_id, s["interval_min"]))
    await answer_callback(call.id)


@router.callback_query(F.data == "int_what")
async def cb_int_what(call: CallbackQuery):
    await answer_callback(call.id,
        "Interval — har bir guruhga xabar yuborish orasidagi vaqt. "
        "Masalan 5 daqiqa = har 5 daqiqada barcha guruhlarga yuboriladi.",
        show_alert=True)


# ═══════════════════════════════════════════════════════════════════
# GURUHLAR — grp_all_, grp_pick_, gtog_, gpg_, grefresh_, grp_back_
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data.startswith("grp_all_"))
async def cb_grp_all(call: CallbackQuery):
    account_id = int(call.data.split("_")[2])
    if not await _check(call, account_id):
        return
    async with db.pool().acquire() as con:
        await con.execute("UPDATE groups SET is_enabled=TRUE WHERE account_id=$1", account_id)
    cnt = await db.count_groups(account_id)
    await answer_callback(call.id, f"✅ Hamma guruh tanlandi ({cnt})", show_alert=True)
    await _show_groups_choice(call, account_id)


@router.callback_query(F.data.startswith("grp_pick_"))
async def cb_grp_pick(call: CallbackQuery):
    account_id = int(call.data.split("_")[2])
    if not await _check(call, account_id):
        return
    await _show_groups_list(call, account_id, 0)


async def _show_groups_choice(call, account_id):
    gc = await db.count_groups(account_id)
    enabled = len(await db.get_enabled_groups(account_id))
    choice = "Hamma guruhlarga" if enabled == gc and gc > 0 else f"{enabled} ta tanlangan"
    text = (
        f"{em.emoji('TARGET')} <b>Guruhlarni sozlash</b>\n\n"
        f"{em.emoji('PIN')} Hozirgi tanlov: <b>{choice}</b>\n\n"
        f"🗒 <b>Guruhlarni tanlang</b>"
    )
    await edit_message(call.message.chat.id, call.message.message_id, text,
                       reply_markup=menus.groups_choice_kb(account_id))


async def _show_groups_list(call, account_id, page):
    groups = await db.get_groups(account_id)
    if not groups:
        text = (f"{em.emoji('CHAT')} <b>Guruhlar</b>\n\n"
                f"Hali guruh yo'q. «🔄 Yangilash» bosing.")
    else:
        enabled = sum(1 for g in groups if g["is_enabled"])
        text = (f"{em.emoji('CHAT')} <b>Guruhlar</b> ({len(groups)} ta)\n\n"
                f"✅ Yoqilgan: <b>{enabled}</b>\n\nYoqish/o'chirish uchun bosing:")
    await edit_message(call.message.chat.id, call.message.message_id, text,
                       reply_markup=menus.groups_list_kb(account_id, groups, page))
    await answer_callback(call.id)


@router.callback_query(F.data.startswith("gtog_"))
async def cb_gtog(call: CallbackQuery):
    _, account_id, group_id = call.data.split("_")
    account_id, group_id = int(account_id), int(group_id)
    groups = await db.get_groups(account_id)
    target = next((g for g in groups if g["id"] == group_id), None)
    if not target:
        await answer_callback(call.id, "❌ Topilmadi")
        return
    new_val = not target["is_enabled"]
    async with db.pool().acquire() as con:
        await con.execute("UPDATE groups SET is_enabled=$1 WHERE id=$2", new_val, group_id)
    await answer_callback(call.id, "✅" if new_val else "⬜")
    await _show_groups_list(call, account_id, 0)


@router.callback_query(F.data.startswith("gpg_"))
async def cb_gpage(call: CallbackQuery):
    _, account_id, page = call.data.split("_")
    await _show_groups_list(call, int(account_id), int(page))


@router.callback_query(F.data.startswith("grefresh_"))
async def cb_grefresh(call: CallbackQuery):
    account_id = int(call.data.split("_")[1])
    account = await _check(call, account_id)
    if not account:
        return
    await answer_callback(call.id, "🔄 Guruhlar yuklanmoqda...")
    groups = await manager.fetch_user_groups(account["session_string"])
    added = 0
    for g in groups:
        if await db.add_group(account_id, g["chat_id"], g["title"]):
            added += 1
    await answer_callback(call.id, f"✅ {added} ta guruh", show_alert=True)
    await _show_groups_list(call, account_id, 0)


@router.callback_query(F.data.startswith("grp_back_"))
async def cb_grp_back(call: CallbackQuery):
    account_id = int(call.data.split("_")[2])
    await _show_groups_choice(call, account_id)
    await answer_callback(call.id)


# ═══════════════════════════════════════════════════════════════════
# AUTOREPLY — reply_on_, reply_off_, reply_text_
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data.startswith("reply_on_"))
async def cb_reply_on(call: CallbackQuery):
    account_id = int(call.data.split("_")[2])
    account = await _check(call, account_id)
    if not account:
        return
    r = await db.get_autoreply(account_id)
    if not r["reply_text"]:
        await answer_callback(call.id, "❌ Avval javob matnini kiriting!", show_alert=True)
        return
    ok = await manager.enable_autoreply(account_id, account["session_string"], r["reply_text"])
    if not ok:
        await answer_callback(call.id, "❌ Akkaunt ulanmadi", show_alert=True)
        return
    await db.update_autoreply(account_id, is_enabled=True)
    await answer_callback(call.id, "🟢 Yoqildi")
    await _show_autoreply(call, account_id)


@router.callback_query(F.data.startswith("reply_off_"))
async def cb_reply_off(call: CallbackQuery):
    account_id = int(call.data.split("_")[2])
    if not await _check(call, account_id):
        return
    await manager.disable_autoreply(account_id)
    await db.update_autoreply(account_id, is_enabled=False)
    await answer_callback(call.id, "🔴 O'chirildi")
    await _show_autoreply(call, account_id)


@router.callback_query(F.data.startswith("reply_text_"))
async def cb_reply_text(call: CallbackQuery, state: FSMContext):
    account_id = int(call.data.split("_")[2])
    if not await _check(call, account_id):
        return
    await state.set_state(AutoReplySetup.waiting_text)
    await state.update_data(account_id=account_id)
    await edit_message(call.message.chat.id, call.message.message_id,
        f"{em.emoji('EDIT')} <b>Autoreply javob matni</b>\n\nAvtomatik yuboriladigan matnni kiriting:",
        reply_markup=menus.inline_back(f"acc_reply_back_{account_id}"))
    await answer_callback(call.id)


@router.message(AutoReplySetup.waiting_text)
async def on_reply_text(message: Message, state: FSMContext):
    data = await state.get_data()
    account_id = data["account_id"]
    text = message.html_text or message.text or ""
    if not text.strip():
        await message.answer(f"{em.emoji('WARN')} Matn bo'sh bo'lmasin.")
        return
    await db.update_autoreply(account_id, reply_text=text)
    await state.clear()
    r = await db.get_autoreply(account_id)
    if r["is_enabled"]:
        account = await db.get_account(account_id)
        await manager.enable_autoreply(account_id, account["session_string"], text)
    await send_message(message.from_user.id,
        f"{em.emoji('OK')} <b>Javob matni saqlandi!</b>",
        reply_markup=menus.autoreply_kb(account_id, r["is_enabled"]))


@router.callback_query(F.data.startswith("acc_reply_back_"))
async def cb_reply_back(call: CallbackQuery, state: FSMContext):
    await state.clear()
    account_id = int(call.data.split("_")[3])
    await _show_autoreply(call, account_id)
    await answer_callback(call.id)


async def _show_autoreply(call, account_id):
    r = await db.get_autoreply(account_id)
    status = "🟢 Yoqilgan" if r["is_enabled"] else f"{em.emoji('RED')} O'chiq"
    cur = r["reply_text"] or "(yo'q)"
    text = (
        f"{em.emoji('CHAT')} <b>Autoreply (DM avto-javob)</b>\n\n"
        f"Holat: <b>{status}</b>\n\n"
        f"Javob matni:\n<blockquote>{cur[:300]}</blockquote>"
    )
    await edit_message(call.message.chat.id, call.message.message_id, text,
                       reply_markup=menus.autoreply_kb(account_id, r["is_enabled"]))


# ═══════════════════════════════════════════════════════════════════
# AKKAUNT STATISTIKASI
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data.startswith("acc_stats_"))
async def cb_acc_stats(call: CallbackQuery):
    account_id = int(call.data.split("_")[2])
    if not await _check(call, account_id):
        return
    st = await db.get_stats(account_id)
    gc = await db.count_groups(account_id)
    text = (
        f"{em.emoji('STATS')} <b>Profil statistikasi</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{em.emoji('CHAT')} Guruhlar: <b>{gc}</b>\n"
        f"📨 Jami urinish: <b>{st['total']}</b>\n"
        f"{em.emoji('OK')} Yuborilgan: <b>{st['sent']}</b>\n"
        f"📅 Bugun: <b>{st['today']}</b>\n"
        f"{em.emoji('CROSS')} Xato: <b>{st['failed']}</b>"
    )
    await edit_message(call.message.chat.id, call.message.message_id, text,
                       reply_markup=menus.inline_back(f"account_{account_id}"))
    await answer_callback(call.id)
