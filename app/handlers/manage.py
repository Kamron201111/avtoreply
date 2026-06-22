"""
Akkaunt boshqaruvi: guruhlar, xabar matni, interval, start/stop, autoreply.
"""
from datetime import datetime, timedelta, timezone

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards import menus
from app.keyboards.builder import btn, kb
from app.states import MessageSetup, AutoReplySetup
from app.userbot import manager
from app import emoji as em
from app.config import config

router = Router(name="manage")


# ═══════════════════════════════════════════════════════════════════
# AKKAUNT KO'RINISHI
# ═══════════════════════════════════════════════════════════════════

async def _account_panel_text(account) -> str:
    s = await db.get_autosend(account["id"])
    gc = await db.count_groups(account["id"])
    enabled_gc = len(await db.get_enabled_groups(account["id"]))
    uname = f"@{account['account_username']}" if account["account_username"] else account["account_name"]
    status = "🟢 Ishlamoqda" if s["is_running"] else "🔴 To'xtagan"
    has_msg = "✅ Sozlangan" if s["message_text"] else "❌ Yo'q"

    return (
        f"{em.eUS()} <b>Akkaunt boshqaruvi</b>\n\n"
        f"👤 Akkaunt: <b>{uname}</b>\n"
        f"📱 Telefon: <code>{account['phone']}</code>\n"
        f"⚙️ Holat: {status}\n\n"
        f"{em.eGR()} Guruhlar: <b>{enabled_gc}</b> / {gc} (yoqilgan/jami)\n"
        f"{em.eCL()} Interval: <b>{s['interval_min']} daqiqa</b>\n"
        f"{em.tg_emoji(em.E_EDIT, '✏️')} Habar matni: {has_msg}\n"
    )


@router.callback_query(F.data.startswith("account_"))
async def cb_account(call: CallbackQuery, state: FSMContext):
    await state.clear()
    account_id = int(call.data.split("_")[1])
    account = await db.get_account(account_id)
    if not account or account["owner_id"] != call.from_user.id:
        await call.answer("❌ Akkaunt topilmadi", show_alert=True)
        return
    s = await db.get_autosend(account_id)
    await call.message.edit_text(
        await _account_panel_text(account),
        reply_markup=menus.account_actions(account_id, s["is_running"]),
    )
    await call.answer()


@router.callback_query(F.data.startswith("del_acc_"))
async def cb_del_account(call: CallbackQuery):
    account_id = int(call.data.split("_")[2])
    account = await db.get_account(account_id)
    if not account or account["owner_id"] != call.from_user.id:
        await call.answer("❌ Topilmadi", show_alert=True)
        return
    await manager.disconnect_client(account_id)
    await db.delete_account(account_id)
    await call.answer("🗑 Akkaunt o'chirildi", show_alert=True)
    accounts = await db.get_accounts(call.from_user.id)
    await call.message.edit_text(
        f"{em.eUS()} <b>Akkauntlar</b>\n\nUlangan: <b>{len(accounts)}</b> ta",
        reply_markup=menus.accounts_menu(accounts),
    )


# ═══════════════════════════════════════════════════════════════════
# START / STOP
# ═══════════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("start_"))
async def cb_start_sending(call: CallbackQuery):
    account_id = int(call.data.split("_")[1])
    account = await db.get_account(account_id)
    if not account or account["owner_id"] != call.from_user.id:
        await call.answer("❌ Topilmadi", show_alert=True)
        return

    s = await db.get_autosend(account_id)
    if not s["message_text"]:
        await call.answer("❌ Avval habar matnini sozlang!", show_alert=True)
        return
    enabled = await db.get_enabled_groups(account_id)
    if not enabled:
        await call.answer("❌ Avval kamida 1 ta guruh tanlang!", show_alert=True)
        return

    next_send = datetime.now(timezone.utc) + timedelta(minutes=s["interval_min"])
    await db.set_running(account_id, True, next_send)
    await call.answer("▶️ Ishga tushdi!", show_alert=True)

    account = await db.get_account(account_id)
    await call.message.edit_text(
        await _account_panel_text(account),
        reply_markup=menus.account_actions(account_id, True),
    )


@router.callback_query(F.data.startswith("stop_"))
async def cb_stop_sending(call: CallbackQuery):
    account_id = int(call.data.split("_")[1])
    account = await db.get_account(account_id)
    if not account or account["owner_id"] != call.from_user.id:
        await call.answer("❌ Topilmadi", show_alert=True)
        return
    await db.set_running(account_id, False)
    await call.answer("⏹ To'xtatildi", show_alert=True)
    account = await db.get_account(account_id)
    await call.message.edit_text(
        await _account_panel_text(account),
        reply_markup=menus.account_actions(account_id, False),
    )


# ═══════════════════════════════════════════════════════════════════
# GURUHLAR
# ═══════════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("acc_groups_"))
async def cb_acc_groups(call: CallbackQuery):
    account_id = int(call.data.split("_")[2])
    await _show_groups(call, account_id, 0)


async def _show_groups(call: CallbackQuery, account_id: int, page: int):
    groups = await db.get_groups(account_id)
    if not groups:
        text = (
            f"{em.eGR()} <b>Guruhlar</b>\n\n"
            f"Hali guruh yo'q.\n\n"
            f"«🔄 Guruhlarni yangilash» tugmasini bosing — "
            f"akkauntingiz a'zo bo'lgan guruhlar avtomatik yuklanadi."
        )
    else:
        enabled = sum(1 for g in groups if g["is_enabled"])
        text = (
            f"{em.eGR()} <b>Guruhlar</b> ({len(groups)} ta)\n\n"
            f"✅ Yoqilgan: <b>{enabled}</b>\n\n"
            f"Guruhni yoqish/o'chirish uchun ustiga bosing:"
        )
    await call.message.edit_text(
        text, reply_markup=menus.groups_kb(account_id, groups, page)
    )
    await call.answer()


@router.callback_query(F.data.startswith("gpage_"))
async def cb_groups_page(call: CallbackQuery):
    _, account_id, page = call.data.split("_")
    await _show_groups(call, int(account_id), int(page))


@router.callback_query(F.data.startswith("togg_"))
async def cb_toggle_group(call: CallbackQuery):
    _, account_id, group_id = call.data.split("_")
    account_id, group_id = int(account_id), int(group_id)
    groups = await db.get_groups(account_id)
    target = next((g for g in groups if g["id"] == group_id), None)
    if not target:
        await call.answer("❌ Topilmadi", show_alert=True)
        return
    new_val = not target["is_enabled"]
    async with db.pool().acquire() as con:
        await con.execute("UPDATE groups SET is_enabled=$1 WHERE id=$2", new_val, group_id)
    await call.answer("✅ Yoqildi" if new_val else "⬜ O'chirildi")
    await _show_groups(call, account_id, 0)


@router.callback_query(F.data.startswith("refresh_groups_"))
async def cb_refresh_groups(call: CallbackQuery):
    account_id = int(call.data.split("_")[2])
    account = await db.get_account(account_id)
    if not account:
        await call.answer("❌ Topilmadi", show_alert=True)
        return
    await call.answer("🔄 Guruhlar yuklanmoqda...")
    groups = await manager.fetch_user_groups(account["session_string"])
    added = 0
    for g in groups:
        if await db.add_group(account_id, g["chat_id"], g["title"]):
            added += 1
    await call.answer(f"✅ {added} ta guruh yangilandi", show_alert=True)
    await _show_groups(call, account_id, 0)


# ═══════════════════════════════════════════════════════════════════
# HABAR MATNI
# ═══════════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("acc_msg_"))
async def cb_set_message(call: CallbackQuery, state: FSMContext):
    account_id = int(call.data.split("_")[2])
    s = await db.get_autosend(account_id)
    await state.set_state(MessageSetup.waiting_text)
    await state.update_data(account_id=account_id)
    current = s["message_text"] or "(yo'q)"
    text = (
        f"{em.tg_emoji(em.E_EDIT, '✏️')} <b>Habar matni</b>\n\n"
        f"Joriy matn:\n<blockquote>{current[:500]}</blockquote>\n\n"
        f"Yangi xabar matnini yuboring.\n\n"
        f"💡 <i>HTML formatlash mumkin: <b>qalin</b>, <i>kursiv</i>, havola va h.k.</i>"
    )
    await call.message.edit_text(
        text, reply_markup=kb([[btn("Orqaga", f"account_{account_id}", emoji=em.E_BACK)]])
    )
    await call.answer()


@router.message(MessageSetup.waiting_text)
async def on_message_text(message: Message, state: FSMContext):
    data = await state.get_data()
    account_id = data["account_id"]
    text = message.html_text or message.text or ""
    if not text.strip():
        await message.answer(f"{em.eWN()} Matn bo'sh bo'lishi mumkin emas.")
        return
    await db.update_autosend(account_id, message_text=text, message_type="text")
    await state.clear()
    account = await db.get_account(account_id)
    s = await db.get_autosend(account_id)
    await message.answer(
        f"{em.eOK()} <b>Habar matni saqlandi!</b>\n\n"
        f"<blockquote>{text[:300]}</blockquote>",
        reply_markup=menus.account_actions(account_id, s["is_running"]),
    )


# ═══════════════════════════════════════════════════════════════════
# INTERVAL
# ═══════════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("acc_int_"))
async def cb_interval(call: CallbackQuery):
    account_id = int(call.data.split("_")[2])
    s = await db.get_autosend(account_id)
    text = (
        f"{em.eCL()} <b>Xabar oralig'i (interval)</b>\n\n"
        f"Joriy interval: <b>{s['interval_min']} daqiqa</b>\n\n"
        f"Kerakli vaqtni tanlang:"
    )
    await call.message.edit_text(
        text, reply_markup=menus.interval_kb(account_id, s["interval_min"])
    )
    await call.answer()


@router.callback_query(F.data.startswith("setint_"))
async def cb_set_interval(call: CallbackQuery):
    _, account_id, minutes = call.data.split("_")
    account_id, minutes = int(account_id), int(minutes)

    # Free tarif cheklovi
    user = await db.get_user(call.from_user.id)
    if not user["is_premium"] and minutes < config.free_min_interval:
        await call.answer(
            f"⚠️ Bepul tarifda minimal interval {config.free_min_interval} daqiqa. "
            f"Premium oling!",
            show_alert=True,
        )
        return

    await db.update_autosend(account_id, interval_min=minutes)
    await call.answer(f"✅ Interval {minutes} daqiqa")
    s = await db.get_autosend(account_id)
    await call.message.edit_text(
        f"{em.eCL()} <b>Xabar oralig'i</b>\n\n"
        f"✅ Yangi interval: <b>{minutes} daqiqa</b>",
        reply_markup=menus.interval_kb(account_id, minutes),
    )


@router.callback_query(F.data.startswith("int_manual_"))
async def cb_int_manual(call: CallbackQuery, state: FSMContext):
    account_id = int(call.data.split("_")[2])
    await state.set_state(MessageSetup.waiting_interval)
    await state.update_data(account_id=account_id)
    await call.message.edit_text(
        f"{em.eCL()} <b>Qo'lda interval kiritish</b>\n\n"
        f"Daqiqalarda son kiriting (masalan: <code>25</code>):",
        reply_markup=kb([[btn("Orqaga", f"acc_int_{account_id}", emoji=em.E_BACK)]]),
    )
    await call.answer()


@router.message(MessageSetup.waiting_interval)
async def on_interval_manual(message: Message, state: FSMContext):
    data = await state.get_data()
    account_id = data["account_id"]
    digits = "".join(c for c in message.text if c.isdigit())
    if not digits:
        await message.answer(f"{em.eWN()} Faqat son kiriting.")
        return
    minutes = int(digits)
    if minutes < 1 or minutes > 1440:
        await message.answer(f"{em.eWN()} Interval 1 — 1440 daqiqa oralig'ida bo'lsin.")
        return

    user = await db.get_user(message.from_user.id)
    if not user["is_premium"] and minutes < config.free_min_interval:
        await message.answer(
            f"⚠️ Bepul tarifda minimal interval {config.free_min_interval} daqiqa."
        )
        return

    await db.update_autosend(account_id, interval_min=minutes)
    await state.clear()
    s = await db.get_autosend(account_id)
    await message.answer(
        f"{em.eOK()} Interval <b>{minutes} daqiqa</b> qilib o'rnatildi!",
        reply_markup=menus.account_actions(account_id, s["is_running"]),
    )


# ═══════════════════════════════════════════════════════════════════
# AUTOREPLY
# ═══════════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("acc_reply_"))
async def cb_autoreply(call: CallbackQuery):
    account_id = int(call.data.split("_")[2])
    r = await db.get_autoreply(account_id)
    status = "🟢 Yoqilgan" if r["is_enabled"] else "🔴 O'chiq"
    current = r["reply_text"] or "(yo'q)"
    text = (
        f"{em.tg_emoji(em.E_CHAT, '💬')} <b>Autoreply (DM avto-javob)</b>\n\n"
        f"Holat: {status}\n\n"
        f"Javob matni:\n<blockquote>{current[:300]}</blockquote>\n\n"
        f"Siz onlayn bo'lmaganingizda kelgan shaxsiy xabarlarga "
        f"avtomatik javob beradi."
    )
    await call.message.edit_text(
        text, reply_markup=menus.autoreply_kb(account_id, r["is_enabled"])
    )
    await call.answer()


@router.callback_query(F.data.startswith("reply_on_"))
async def cb_reply_on(call: CallbackQuery):
    account_id = int(call.data.split("_")[2])
    r = await db.get_autoreply(account_id)
    if not r["reply_text"]:
        await call.answer("❌ Avval javob matnini kiriting!", show_alert=True)
        return
    account = await db.get_account(account_id)
    ok = await manager.enable_autoreply(account_id, account["session_string"], r["reply_text"])
    if not ok:
        await call.answer("❌ Akkaunt ulanmadi", show_alert=True)
        return
    await db.update_autoreply(account_id, is_enabled=True)
    await call.answer("🟢 Autoreply yoqildi")
    await cb_autoreply(call)


@router.callback_query(F.data.startswith("reply_off_"))
async def cb_reply_off(call: CallbackQuery):
    account_id = int(call.data.split("_")[2])
    await manager.disable_autoreply(account_id)
    await db.update_autoreply(account_id, is_enabled=False)
    await call.answer("🔴 Autoreply o'chirildi")
    await cb_autoreply(call)


@router.callback_query(F.data.startswith("reply_text_"))
async def cb_reply_text(call: CallbackQuery, state: FSMContext):
    account_id = int(call.data.split("_")[2])
    await state.set_state(AutoReplySetup.waiting_text)
    await state.update_data(account_id=account_id)
    await call.message.edit_text(
        f"💬 <b>Autoreply javob matni</b>\n\n"
        f"Avtomatik yuboriladigan javob matnini kiriting:",
        reply_markup=kb([[btn("Orqaga", f"acc_reply_{account_id}", emoji=em.E_BACK)]]),
    )
    await call.answer()


@router.message(AutoReplySetup.waiting_text)
async def on_reply_text(message: Message, state: FSMContext):
    data = await state.get_data()
    account_id = data["account_id"]
    text = message.html_text or message.text or ""
    if not text.strip():
        await message.answer(f"{em.eWN()} Matn bo'sh bo'lmasin.")
        return
    await db.update_autoreply(account_id, reply_text=text)
    await state.clear()
    r = await db.get_autoreply(account_id)
    # Agar yoqilgan bo'lsa, handlerni yangilaymiz
    if r["is_enabled"]:
        account = await db.get_account(account_id)
        await manager.enable_autoreply(account_id, account["session_string"], text)
    await message.answer(
        f"{em.eOK()} <b>Javob matni saqlandi!</b>",
        reply_markup=menus.autoreply_kb(account_id, r["is_enabled"]),
    )


# ═══════════════════════════════════════════════════════════════════
# AKKAUNT STATISTIKASI
# ═══════════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("acc_stats_"))
async def cb_acc_stats(call: CallbackQuery):
    account_id = int(call.data.split("_")[2])
    st = await db.get_stats(account_id)
    gc = await db.count_groups(account_id)
    text = (
        f"{em.eST()} <b>Akkaunt statistikasi</b>\n\n"
        f"{em.eGR()} Guruhlar: <b>{gc}</b>\n"
        f"📨 Jami urinishlar: <b>{st['total']}</b>\n"
        f"✅ Muvaffaqiyatli: <b>{st['sent']}</b>\n"
        f"📅 Bugun yuborilgan: <b>{st['today']}</b>\n"
        f"❌ Xato: <b>{st['failed']}</b>\n"
    )
    await call.message.edit_text(
        text, reply_markup=kb([[btn("Orqaga", f"account_{account_id}", emoji=em.E_BACK)]])
    )
    await call.answer()


# Asosiy menyudagi yorliqlar — akkaunt tanlashga yo'naltirish
@router.callback_query(F.data.in_({"autosend_menu", "set_message", "set_interval",
                                    "groups_menu", "autoreply_menu"}))
async def cb_need_account(call: CallbackQuery):
    accounts = await db.get_accounts(call.from_user.id)
    if not accounts:
        await call.message.edit_text(
            f"{em.eWN()} <b>Avval akkaunt ulang!</b>\n\n"
            f"Bu funksiyadan foydalanish uchun kamida bitta akkaunt ulashingiz kerak.",
            reply_markup=kb([
                [btn("➕ Akkaunt qo'shish", "add_account", style="success")],
                [btn("Orqaga", "back_main", emoji=em.E_BACK)],
            ]),
        )
        await call.answer()
        return
    # Akkauntlar bo'lsa — ro'yxatni ko'rsatamiz
    await call.message.edit_text(
        f"{em.eUS()} <b>Akkauntni tanlang</b>\n\nQuyidagilardan birini tanlang:",
        reply_markup=menus.accounts_menu(accounts),
    )
    await call.answer()
