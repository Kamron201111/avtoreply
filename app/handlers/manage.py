"""
Akkaunt boshqaruvi + DM javob + Autoreply callbacklari — 3 tilli, raw API.
"""
import json
from datetime import datetime, timedelta, timezone

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards import menus, reply
from app.raw_api import send_message, edit_message, answer_callback, delete_message
from app.states import MessageSetup, AutoReplySetup, DMReplySetup, GroupReplySetup
from app.userbot import manager
from app.i18n import t, TEXTS
from app.lang_util import get_lang
from app import emoji as em
from app.config import config

router = Router(name="manage")


def _is_btn(text, key):
    from app.i18n import is_button
    return is_button(text, key)


async def _panel_text(account, lang):
    from app.handlers.menu import account_panel_text
    return await account_panel_text(account, lang)


async def _check(call, account_id):
    account = await db.get_account(account_id)
    if not account or account["owner_id"] != call.from_user.id:
        await answer_callback(call.id, "❌", show_alert=True)
        return None
    return account


# ═══ AKKAUNT PANEL ═══
@router.callback_query(F.data.startswith("account_"))
async def cb_account(call: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = await get_lang(call.from_user.id)
    account_id = int(call.data.split("_")[1])
    account = await _check(call, account_id)
    if not account:
        return
    s = await db.get_autosend(account_id)
    await edit_message(call.message.chat.id, call.message.message_id,
                       await _panel_text(account, lang),
                       reply_markup=menus.account_panel(account_id, s["is_running"], s["mention_enabled"], lang))
    await answer_callback(call.id)


# ═══ START / STOP ═══
@router.callback_query(F.data.startswith("start_"))
async def cb_start(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    account_id = int(call.data.split("_")[1])
    account = await _check(call, account_id)
    if not account:
        return
    s = await db.get_autosend(account_id)
    if not s["message_text"]:
        await answer_callback(call.id, t("need_msg", lang), show_alert=True)
        return
    if not await db.get_enabled_groups(account_id):
        await answer_callback(call.id, t("need_groups", lang), show_alert=True)
        return
    nxt = datetime.now(timezone.utc) + timedelta(minutes=s["interval_min"])
    await db.set_running(account_id, True, nxt)
    await answer_callback(call.id, t("started", lang), show_alert=True)
    account = await db.get_account(account_id)
    await edit_message(call.message.chat.id, call.message.message_id,
                       await _panel_text(account, lang),
                       reply_markup=menus.account_panel(account_id, True, s["mention_enabled"], lang))


@router.callback_query(F.data.startswith("stop_"))
async def cb_stop(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    account_id = int(call.data.split("_")[1])
    if not await _check(call, account_id):
        return
    await db.set_running(account_id, False)
    await answer_callback(call.id, t("stopped", lang), show_alert=True)
    s = await db.get_autosend(account_id)
    account = await db.get_account(account_id)
    await edit_message(call.message.chat.id, call.message.message_id,
                       await _panel_text(account, lang),
                       reply_markup=menus.account_panel(account_id, False, s["mention_enabled"], lang))


# ═══ MENTION (ogohlantirish bilan) ═══
@router.callback_query(F.data.startswith("acc_mention_"))
async def cb_mention(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    account_id = int(call.data.split("_")[2])
    if not await _check(call, account_id):
        return
    s = await db.get_autosend(account_id)
    if s["mention_enabled"]:
        # O'chirish — to'g'ridan-to'g'ri
        await db.update_autosend(account_id, mention_enabled=False)
        await answer_callback(call.id, t("off", lang))
        account = await db.get_account(account_id)
        await edit_message(call.message.chat.id, call.message.message_id,
                           await _panel_text(account, lang),
                           reply_markup=menus.account_panel(account_id, s["is_running"], False, lang))
    else:
        # Yoqishdan oldin ogohlantirish (Image 4)
        await edit_message(call.message.chat.id, call.message.message_id,
                           t("mention_warn", lang),
                           reply_markup=menus.mention_warn_kb(account_id, lang))
    await answer_callback(call.id)


@router.callback_query(F.data.startswith("mention_yes_"))
async def cb_mention_yes(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    account_id = int(call.data.split("_")[2])
    if not await _check(call, account_id):
        return
    await db.update_autosend(account_id, mention_enabled=True)
    await answer_callback(call.id, t("on", lang), show_alert=True)
    s = await db.get_autosend(account_id)
    account = await db.get_account(account_id)
    await edit_message(call.message.chat.id, call.message.message_id,
                       await _panel_text(account, lang),
                       reply_markup=menus.account_panel(account_id, s["is_running"], True, lang))


# ═══ AVTO-O'CHIRISH TAYMERI ═══
@router.callback_query(F.data.startswith("acc_timer_"))
async def cb_timer(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    await answer_callback(call.id, t("soon", lang), show_alert=True)


# ═══ AKKAUNTNI O'CHIRISH ═══
@router.callback_query(F.data.startswith("del_acc_"))
async def cb_del(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    account_id = int(call.data.split("_")[2])
    if not await _check(call, account_id):
        return
    await manager.disconnect_client(account_id)
    await db.delete_account(account_id)
    await answer_callback(call.id, t("acc_deleted", lang), show_alert=True)
    accounts = await db.get_accounts(call.from_user.id)
    body = t("prof_count", lang, n=len(accounts)) if accounts else t("prof_none", lang)
    await edit_message(call.message.chat.id, call.message.message_id,
                       f"{t('prof_title', lang)}\n\n{body}",
                       reply_markup=menus.accounts_menu(accounts, lang))


# ═══ HABAR TURI ═══
@router.callback_query(F.data.startswith("mtype_text_"))
async def cb_mtype_text(call: CallbackQuery, state: FSMContext):
    lang = await get_lang(call.from_user.id)
    account_id = int(call.data.split("_")[2])
    if not await _check(call, account_id):
        return
    await db.update_autosend(account_id, message_type="text")
    await state.set_state(MessageSetup.waiting_text)
    await state.update_data(account_id=account_id)
    await edit_message(call.message.chat.id, call.message.message_id,
                       t("send_text", lang), reply_markup=menus.inline_back(f"account_{account_id}", lang))
    await answer_callback(call.id)


@router.callback_query(F.data.startswith("mtype_photo_"))
async def cb_mtype_photo(call: CallbackQuery, state: FSMContext):
    lang = await get_lang(call.from_user.id)
    account_id = int(call.data.split("_")[2])
    if not await _check(call, account_id):
        return
    await db.update_autosend(account_id, message_type="photo")
    await state.set_state(MessageSetup.waiting_text)
    await state.update_data(account_id=account_id, want_photo=True)
    await edit_message(call.message.chat.id, call.message.message_id,
                       t("send_photo", lang), reply_markup=menus.inline_back(f"account_{account_id}", lang))
    await answer_callback(call.id)


@router.callback_query(F.data.startswith("mtype_btn_"))
async def cb_mtype_btn(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    await answer_callback(call.id, t("soon", lang), show_alert=True)


@router.callback_query(F.data.startswith("mtype_fwd_"))
async def cb_mtype_fwd(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    user = await db.get_user(call.from_user.id)
    if not (user and user["is_premium"]):
        await answer_callback(call.id, t("pro_only", lang), show_alert=True)
        return
    await answer_callback(call.id, t("soon", lang), show_alert=True)


@router.callback_query(F.data.startswith("mtype_multi_"))
async def cb_mtype_multi(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    user = await db.get_user(call.from_user.id)
    if not (user and user["is_premium"]):
        await answer_callback(call.id, t("pro_only", lang), show_alert=True)
        return
    await answer_callback(call.id, t("soon", lang), show_alert=True)


@router.message(MessageSetup.waiting_text)
async def on_msg_text(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    data = await state.get_data()
    account_id = data["account_id"]
    want_photo = data.get("want_photo", False)
    file_id = ""
    if want_photo:
        if not message.photo:
            await message.answer(t("send_photo", lang))
            return
        file_id = message.photo[-1].file_id
        text = message.html_text or message.caption or ""
    else:
        text = message.html_text or message.text or ""
    if not text.strip() and not file_id:
        await message.answer(t("only_number", lang))
        return
    await db.update_autosend(account_id, message_text=text, message_file_id=file_id)
    await state.clear()
    s = await db.get_autosend(account_id)
    account = await db.get_account(account_id)
    await send_message(message.from_user.id,
                       f"{t('msg_saved', lang)}\n\n<blockquote>{text[:300]}</blockquote>",
                       reply_markup=menus.account_panel(account_id, s["is_running"], s["mention_enabled"], lang))


# ═══ INTERVAL ═══
@router.callback_query(F.data.startswith("setint_"))
async def cb_setint(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    _, account_id, minutes = call.data.split("_")
    account_id, minutes = int(account_id), int(minutes)
    if not await _check(call, account_id):
        return
    user = await db.get_user(call.from_user.id)
    if not user["is_premium"] and minutes < config.free_min_interval:
        await answer_callback(call.id, t("int_free_limit", lang, n=config.free_min_interval), show_alert=True)
        return
    await db.update_autosend(account_id, interval_min=minutes)
    await answer_callback(call.id, t("int_set", lang, n=minutes))
    unit = "daqiqa" if lang == "uz" else "мин" if lang == "ru" else "min"
    await edit_message(call.message.chat.id, call.message.message_id,
                       f"{em.emoji('TIMER')} <b>{t('int_title', lang)}</b>\n\n{t('int_cur', lang)}: <b>{minutes} {unit}</b>\n\n{t('int_choose', lang)}",
                       reply_markup=menus.interval_kb(account_id, minutes, lang))


@router.callback_query(F.data.startswith("int_manual_"))
async def cb_int_manual(call: CallbackQuery, state: FSMContext):
    lang = await get_lang(call.from_user.id)
    account_id = int(call.data.split("_")[2])
    if not await _check(call, account_id):
        return
    await state.set_state(MessageSetup.waiting_interval)
    await state.update_data(account_id=account_id)
    await edit_message(call.message.chat.id, call.message.message_id,
                       t("int_manual_q", lang), reply_markup=menus.inline_back(f"intback_{account_id}", lang))
    await answer_callback(call.id)


@router.message(MessageSetup.waiting_interval)
async def on_int_manual(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    data = await state.get_data()
    account_id = data["account_id"]
    digits = "".join(c for c in message.text if c.isdigit())
    if not digits:
        await message.answer(t("only_number", lang))
        return
    minutes = int(digits)
    if minutes < 1 or minutes > 1440:
        await message.answer(t("only_number", lang))
        return
    user = await db.get_user(message.from_user.id)
    if not user["is_premium"] and minutes < config.free_min_interval:
        await message.answer(t("int_free_limit", lang, n=config.free_min_interval))
        return
    await db.update_autosend(account_id, interval_min=minutes)
    await state.clear()
    s = await db.get_autosend(account_id)
    await send_message(message.from_user.id, t("int_set", lang, n=minutes),
                       reply_markup=menus.account_panel(account_id, s["is_running"], s["mention_enabled"], lang))


@router.callback_query(F.data.startswith("intback_"))
async def cb_intback(call: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = await get_lang(call.from_user.id)
    account_id = int(call.data.split("_")[1])
    s = await db.get_autosend(account_id)
    unit = "daqiqa" if lang == "uz" else "мин" if lang == "ru" else "min"
    await edit_message(call.message.chat.id, call.message.message_id,
                       f"{em.emoji('TIMER')} <b>{t('int_title', lang)}</b>\n\n{t('int_cur', lang)}: <b>{s['interval_min']} {unit}</b>\n\n{t('int_choose', lang)}",
                       reply_markup=menus.interval_kb(account_id, s["interval_min"], lang))
    await answer_callback(call.id)


@router.callback_query(F.data == "int_what")
async def cb_int_what(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    await answer_callback(call.id, t("int_what", lang), show_alert=True)


# ═══ GURUHLAR ═══
@router.callback_query(F.data.startswith("grp_all_"))
async def cb_grp_all(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    account_id = int(call.data.split("_")[2])
    if not await _check(call, account_id):
        return
    await db.enable_all_groups(account_id, True)
    cnt = await db.count_groups(account_id)
    await answer_callback(call.id, t("grp_all_on", lang), show_alert=True)
    await _show_groups_choice(call, account_id, lang)


@router.callback_query(F.data.startswith("grp_pick_"))
async def cb_grp_pick(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    account_id = int(call.data.split("_")[2])
    if not await _check(call, account_id):
        return
    # Image 6: pastdagi 3ta (Ro'yxatlar/Qo'shish/O'chirish)
    await edit_message(call.message.chat.id, call.message.message_id,
                       f"{t('grp_title', lang)}\n\n{t('grp_choose', lang)}",
                       reply_markup=menus.groups_pick_kb(account_id, lang))
    await answer_callback(call.id)


async def _show_groups_choice(call, account_id, lang):
    gc = await db.count_groups(account_id)
    enabled = len(await db.get_enabled_groups(account_id))
    choice = t("grp_all_lbl", lang) if (enabled == gc and gc > 0) else t("grp_count", lang, n=enabled)
    text = (f"{t('grp_title', lang)}\n\n{em.emoji('PIN')} {t('grp_cur', lang)}: <b>{choice}</b>\n\n{t('grp_choose', lang)}")
    await edit_message(call.message.chat.id, call.message.message_id, text,
                       reply_markup=menus.groups_choice_kb(account_id, lang))


# Ro'yxatlar — tanlangan guruhlarni ko'rsatish/toggle
@router.callback_query(F.data.startswith("glist_"))
async def cb_glist(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    account_id = int(call.data.split("_")[1])
    await _show_groups_list(call, account_id, 0, lang)


# Qo'shish — guruhlarni yangilab yuklash
@router.callback_query(F.data.startswith("gadd_"))
async def cb_gadd(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    account_id = int(call.data.split("_")[1])
    account = await _check(call, account_id)
    if not account:
        return
    await answer_callback(call.id, t("grp_loading", lang))
    groups = await manager.fetch_user_groups(account["session_string"])
    added = 0
    for g in groups:
        if await db.add_group(account_id, g["chat_id"], g["title"]):
            added += 1
    await answer_callback(call.id, t("grp_loaded", lang, n=added), show_alert=True)
    await _show_groups_list(call, account_id, 0, lang)


# O'chirish — hammasini o'chirish
@router.callback_query(F.data.startswith("gdel_"))
async def cb_gdel(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    account_id = int(call.data.split("_")[1])
    if not await _check(call, account_id):
        return
    await db.clear_groups(account_id)
    await answer_callback(call.id, t("grp_cleared", lang), show_alert=True)
    await _show_groups_list(call, account_id, 0, lang)


async def _show_groups_list(call, account_id, page, lang):
    groups = await db.get_groups(account_id)
    if not groups:
        text = f"{em.emoji('GROUP')} <b>{t('p_groups', lang)}</b>\n\n{t('grp_empty', lang)}"
    else:
        enabled = sum(1 for g in groups if g["is_enabled"])
        text = (f"{em.emoji('GROUP')} <b>{t('p_groups', lang)}</b> ({len(groups)})\n\n"
                f"✅ {enabled}\n\n{t('grp_choose', lang)}")
    await edit_message(call.message.chat.id, call.message.message_id, text,
                       reply_markup=menus.groups_list_kb(account_id, groups, page, 8, lang))
    await answer_callback(call.id)


@router.callback_query(F.data.startswith("gtog_"))
async def cb_gtog(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    _, account_id, group_id = call.data.split("_")
    account_id, group_id = int(account_id), int(group_id)
    groups = await db.get_groups(account_id)
    target = next((g for g in groups if g["id"] == group_id), None)
    if not target:
        await answer_callback(call.id, "❌")
        return
    await db.set_group_enabled(group_id, not target["is_enabled"])
    await answer_callback(call.id, "✅" if not target["is_enabled"] else "⬜")
    await _show_groups_list(call, account_id, 0, lang)


@router.callback_query(F.data.startswith("gpg_"))
async def cb_gpage(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    _, account_id, page = call.data.split("_")
    await _show_groups_list(call, int(account_id), int(page), lang)


@router.callback_query(F.data.startswith("grefresh_"))
async def cb_grefresh(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    account_id = int(call.data.split("_")[1])
    account = await _check(call, account_id)
    if not account:
        return
    await answer_callback(call.id, t("grp_loading", lang))
    groups = await manager.fetch_user_groups(account["session_string"])
    added = 0
    for g in groups:
        if await db.add_group(account_id, g["chat_id"], g["title"]):
            added += 1
    await answer_callback(call.id, t("grp_loaded", lang, n=added), show_alert=True)
    await _show_groups_list(call, account_id, 0, lang)


@router.callback_query(F.data.startswith("gpick_back_"))
async def cb_gpick_back(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    account_id = int(call.data.split("_")[2])
    await edit_message(call.message.chat.id, call.message.message_id,
                       f"{t('grp_title', lang)}\n\n{t('grp_choose', lang)}",
                       reply_markup=menus.groups_pick_kb(account_id, lang))
    await answer_callback(call.id)


@router.callback_query(F.data.startswith("grp_back_"))
async def cb_grp_back(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    account_id = int(call.data.split("_")[2])
    await _show_groups_choice(call, account_id, lang)
    await answer_callback(call.id)


# ═══ AKKAUNT STATISTIKASI ═══
@router.callback_query(F.data.startswith("acc_stats_"))
async def cb_acc_stats(call: CallbackQuery):
    lang = await get_lang(call.from_user.id)
    account_id = int(call.data.split("_")[2])
    if not await _check(call, account_id):
        return
    st = await db.get_stats(account_id)
    gc = await db.count_groups(account_id)
    text = (f"{t('stat_title', lang)}\n━━━━━━━━━━━━━━━━━━━━\n"
            f"{em.emoji('GROUP')} {t('p_groups', lang)}: <b>{gc}</b>\n"
            f"{em.emoji('OK')} {t('cab_total', lang)}: <b>{st['sent']}</b>\n"
            f"📅 {t('cab_today', lang)}: <b>{st['today']}</b>\n"
            f"❌ {st['failed']}")
    await edit_message(call.message.chat.id, call.message.message_id, text,
                       reply_markup=menus.inline_back(f"account_{account_id}", lang))
    await answer_callback(call.id)


# ═══════════════════════════════════════════════════════════════════
# DM JAVOB — reply keyboard tugmalari (Image 9)
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "dm_b_run"))
async def dm_run(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    account = await _first_account(message.from_user.id)
    if not account:
        await send_message(message.from_user.id, t("no_account", lang))
        return
    r = await db.get_dm_reply(account["id"])
    if not r["is_enabled"]:
        if not r["reply_text"]:
            await send_message(message.from_user.id, t("need_msg", lang))
            return
        ok = await manager.enable_dm_reply(account["id"], account["session_string"], r["reply_text"])
        if not ok:
            await send_message(message.from_user.id, t("st_stopped", lang))
            return
        await db.update_dm_reply(account["id"], is_enabled=True)
        await send_message(message.from_user.id, t("started", lang))
    else:
        await manager.disable_dm_reply(account["id"])
        await db.update_dm_reply(account["id"], is_enabled=False)
        await send_message(message.from_user.id, t("stopped", lang))


@router.message(lambda m: _is_btn(m.text, "dm_b_setmsg"))
async def dm_setmsg(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    account = await _first_account(message.from_user.id)
    if not account:
        await send_message(message.from_user.id, t("no_account", lang))
        return
    await state.set_state(DMReplySetup.waiting_text)
    await state.update_data(account_id=account["id"])
    await send_message(message.from_user.id, t("dm_send_text", lang))


@router.message(DMReplySetup.waiting_text)
async def dm_on_text(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    data = await state.get_data()
    account_id = data["account_id"]
    text = message.html_text or message.text or ""
    if not text.strip():
        await message.answer(t("only_number", lang))
        return
    await db.update_dm_reply(account_id, reply_text=text)
    await state.clear()
    r = await db.get_dm_reply(account_id)
    if r["is_enabled"]:
        account = await db.get_account(account_id)
        await manager.enable_dm_reply(account_id, account["session_string"], text)
    await send_message(message.from_user.id, t("msg_saved", lang),
                       reply_markup=reply.dm_reply_keyboard(lang))


# ═══════════════════════════════════════════════════════════════════
# AUTOREPLY — reply keyboard tugmalari (Image 12)
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "ar_run"))
async def ar_run(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    account = await _first_account(message.from_user.id)
    if not account:
        await send_message(message.from_user.id, t("no_account", lang))
        return
    gr = await db.get_group_reply(account["id"])
    if not gr["is_enabled"]:
        if not gr["reply_text"]:
            await send_message(message.from_user.id, t("need_msg", lang))
            return
        ok = await manager.enable_group_reply(account["id"], account["session_string"],
                                              gr["reply_text"], json.loads(gr["groups_json"] or "[]"))
        if not ok:
            await send_message(message.from_user.id, t("st_stopped", lang))
            return
        await db.update_group_reply(account["id"], is_enabled=True)
        await send_message(message.from_user.id, t("started", lang))
    else:
        await manager.disable_group_reply(account["id"])
        await db.update_group_reply(account["id"], is_enabled=False)
        await send_message(message.from_user.id, t("stopped", lang))


@router.message(lambda m: _is_btn(m.text, "ar_replymsg"))
async def ar_setmsg(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    account = await _first_account(message.from_user.id)
    if not account:
        await send_message(message.from_user.id, t("no_account", lang))
        return
    await state.set_state(GroupReplySetup.waiting_text)
    await state.update_data(account_id=account["id"])
    await send_message(message.from_user.id, t("ar_send_text", lang))


@router.message(GroupReplySetup.waiting_text)
async def ar_on_text(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    data = await state.get_data()
    account_id = data["account_id"]
    text = message.html_text or message.text or ""
    if not text.strip():
        await message.answer(t("only_number", lang))
        return
    await db.update_group_reply(account_id, reply_text=text)
    await state.clear()
    await send_message(message.from_user.id, t("msg_saved", lang),
                       reply_markup=reply.autoreply_keyboard(lang))


@router.message(lambda m: _is_btn(m.text, "ar_replygrp"))
async def ar_setgroups(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    account = await _first_account(message.from_user.id)
    if not account:
        await send_message(message.from_user.id, t("no_account", lang))
        return
    await state.set_state(GroupReplySetup.waiting_groups)
    await state.update_data(account_id=account["id"])
    await send_message(message.from_user.id, t("ar_send_groups", lang))


@router.message(GroupReplySetup.waiting_groups)
async def ar_on_groups(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    data = await state.get_data()
    account_id = data["account_id"]
    # username larni ajratamiz
    usernames = []
    for line in message.text.split("\n"):
        u = line.strip().lstrip("@")
        if u:
            usernames.append(u)
    await db.update_group_reply(account_id, groups_json=json.dumps(usernames))
    await state.clear()
    gr = await db.get_group_reply(account_id)
    if gr["is_enabled"]:
        account = await db.get_account(account_id)
        await manager.enable_group_reply(account_id, account["session_string"], gr["reply_text"], usernames)
    await send_message(message.from_user.id,
                       f"{t('msg_saved', lang)} ({len(usernames)})",
                       reply_markup=reply.autoreply_keyboard(lang))


@router.message(lambda m: _is_btn(m.text, "ar_dontsend"))
async def ar_dontsend(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    account = await _first_account(message.from_user.id)
    if account:
        await manager.disable_group_reply(account["id"])
        await db.update_group_reply(account["id"], is_enabled=False)
    await send_message(message.from_user.id, t("stopped", lang),
                       reply_markup=reply.autoreply_keyboard(lang))


@router.message(lambda m: _is_btn(m.text, "ar_settings"))
async def ar_settings(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    await send_message(message.from_user.id,
                       f"{em.emoji('GEAR')} {t('ar_settings', lang)}\n\n{t('soon', lang)}",
                       reply_markup=reply.autoreply_keyboard(lang))
