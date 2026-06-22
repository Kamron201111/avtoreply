"""
Asosiy menyu bo'limlari — 3 tilli, raw API, premium emoji + rang.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards import reply, menus
from app.raw_api import send_message, edit_message, answer_callback, delete_message
from app.i18n import t, TEXTS
from app.lang_util import get_lang
from app import emoji as em
from app.config import config

router = Router(name="menu")


# ─── Tugma matnini har 3 tilda solishtirish ────────────────────────
def _is_btn(text: str, key: str) -> bool:
    """Berilgan matn shu key ning biror tildagi varianti bilan boshlanadimi."""
    if not text:
        return False
    variants = TEXTS.get(key, {})
    return any(text == v for v in variants.values())


async def account_panel_text(account, lang="uz") -> str:
    s = await db.get_autosend(account["id"])
    gc = await db.count_groups(account["id"])
    name = account["account_name"] or account["phone"] or f"#{account['id']}"
    status = t("st_running", lang) if s["is_running"] else t("st_stopped", lang)
    mtype_key = {"text": "mtype_text", "photo": "mtype_photo", "button": "mtype_button"}.get(
        s["message_type"], "mtype_text")
    auto_del = t("infinite", lang) if s["auto_delete_sec"] == 0 else f"{s['auto_delete_sec']}s"
    mention = t("on", lang) if s["mention_enabled"] else t("off", lang)
    return (
        f"{em.emoji('USER')} <b>{t('panel_title', lang)}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{em.emoji('USERS')} {t('p_profile', lang)}: <b>{name}</b>\n"
        f"{em.emoji('RED')} {t('p_status', lang)}: <b>{status}</b>\n"
        f"{em.emoji('USER')} {t('p_msgtype', lang)}: <b>{t(mtype_key, lang)}</b>\n"
        f"{em.emoji('GROUP')} {t('p_groups', lang)}: <b>{gc}</b>\n"
        f"{em.emoji('CLOCK')} {t('p_interval', lang)}: <b>{s['interval_min']} {('daqiqa' if lang=='uz' else 'мин' if lang=='ru' else 'min')}</b>\n"
        f"{em.emoji('TIMER')} {t('p_autodel', lang)}: <b>{auto_del}</b>\n"
        f"{em.emoji('MENTION')} {t('p_mention', lang)}: <b>{mention}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )


async def _first_account(user_id):
    accounts = await db.get_accounts(user_id)
    return accounts[0] if accounts else None


# ═══════════════════════════════════════════════════════════════════
# 1. AUTOHABAR YUBORISH
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "btn_autosend"))
async def m_autosend(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    account = await _first_account(message.from_user.id)
    if not account:
        await send_message(message.from_user.id, t("no_account", lang))
        return
    s = await db.get_autosend(account["id"])
    await send_message(message.from_user.id, await account_panel_text(account, lang),
                       reply_markup=menus.account_panel(account["id"], s["is_running"], s["mention_enabled"], lang))


# ═══════════════════════════════════════════════════════════════════
# 2. HABAR MATNI
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "btn_message"))
async def m_message(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    account = await _first_account(message.from_user.id)
    if not account:
        await send_message(message.from_user.id, t("no_account", lang))
        return
    s = await db.get_autosend(account["id"])
    mtype_key = {"text": "mtype_text", "photo": "mtype_photo", "button": "mtype_button"}.get(
        s["message_type"], "mtype_text")
    has_msg = t("msg_set", lang) if s["message_text"] else t("msg_notset", lang)
    text = (
        f"{em.emoji('USER')} <b>{t('msg_title', lang)}</b>\n\n"
        f"📄 {t('msg_curtype', lang)}: <b>{t(mtype_key, lang)}</b>\n"
        f"📝 {t('msg_msg', lang)}: <b>{has_msg}</b>\n\n"
        f"{t('fwd_pro', lang)}\n\n"
        f"{t('choose_msgtype', lang)}"
    )
    await send_message(message.from_user.id, text,
                       reply_markup=menus.message_type_kb(account["id"], lang))


# ═══════════════════════════════════════════════════════════════════
# 3. INTERVAL
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "btn_interval"))
async def m_interval(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    account = await _first_account(message.from_user.id)
    if not account:
        await send_message(message.from_user.id, t("no_account", lang))
        return
    s = await db.get_autosend(account["id"])
    unit = "daqiqa" if lang == "uz" else "мин" if lang == "ru" else "min"
    text = (
        f"{em.emoji('TIMER')} <b>{t('int_title', lang)}</b>\n\n"
        f"{t('int_cur', lang)}: <b>{s['interval_min']} {unit}</b>\n\n"
        f"{t('int_choose', lang)}"
    )
    await send_message(message.from_user.id, text,
                       reply_markup=menus.interval_kb(account["id"], s["interval_min"], lang))


# ═══════════════════════════════════════════════════════════════════
# 4. GURUHLARNI SOZLASH
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "btn_groups"))
async def m_groups(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    account = await _first_account(message.from_user.id)
    if not account:
        await send_message(message.from_user.id, t("no_account", lang))
        return
    gc = await db.count_groups(account["id"])
    enabled = len(await db.get_enabled_groups(account["id"]))
    choice = t("grp_all_lbl", lang) if (enabled == gc and gc > 0) else t("grp_count", lang, n=enabled)
    text = (
        f"{t('grp_title', lang)}\n\n"
        f"{t('grp_q', lang)}\n"
        f"✔️ {t('grp_selected', lang)}\n➕ {t('grp_notselected', lang)}\n\n"
        f"{em.emoji('PIN')} {t('grp_cur', lang)}: <b>{choice}</b>\n\n"
        f"{t('grp_choose', lang)}"
    )
    await send_message(message.from_user.id, text,
                       reply_markup=menus.groups_choice_kb(account["id"], lang))


# ═══════════════════════════════════════════════════════════════════
# 5. PROFILLAR
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "btn_profiles"))
async def m_profiles(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    accounts = await db.get_accounts(message.from_user.id)
    body = (t("prof_count", lang, n=len(accounts)) + "\n\n" + t("prof_manage", lang)) if accounts else t("prof_none", lang)
    await send_message(message.from_user.id, f"{t('prof_title', lang)}\n\n{body}",
                       reply_markup=menus.accounts_menu(accounts, lang))


# ═══════════════════════════════════════════════════════════════════
# 6. PRO TARIF
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "btn_pro"))
async def m_pro(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    user = await db.get_user(message.from_user.id)
    is_prem = user["is_premium"] if user else False
    pc = await db.get_setting("pro_price_card", "50000")
    ps = await db.get_setting("pro_price_stars", "500")
    status = t("pro_active", lang) if is_prem else t("pro_free", lang)
    som = "so'm" if lang == "uz" else "сум" if lang == "ru" else "UZS"
    text = (
        f"{t('pro_title', lang)}\n━━━━━━━━━━━━━━━━━━━━\n"
        f"{t('pro_your', lang)}: {status}\n\n"
        f"{t('pro_feats', lang)}\n\n"
        f"💳 {int(pc):,} {som}\n⭐️ {ps} ⭐\n\n"
        f"{t('pro_gift_hint', lang)}"
    )
    await send_message(message.from_user.id, text, reply_markup=menus.pro_kb(is_prem, lang))


# ═══════════════════════════════════════════════════════════════════
# 7. KABINET
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "btn_cabinet"))
async def m_cabinet(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    user = await db.get_user(message.from_user.id)
    accounts = await db.get_accounts(message.from_user.id)
    is_prem = user["is_premium"] if user else False
    total_sent = total_today = total_groups = 0
    interval = 5
    for a in accounts:
        st = await db.get_stats(a["id"])
        total_sent += st["sent"]; total_today += st["today"]
        total_groups += await db.count_groups(a["id"])
        s = await db.get_autosend(a["id"]); interval = s["interval_min"]
    first = accounts[0] if accounts else None
    name = first["account_name"] if first else (user["full_name"] if user else "—")
    phone = first["phone"] if first else "—"
    uname = f"@{first['account_username']}" if first and first["account_username"] else "—"
    unit = "daqiqa" if lang == "uz" else "мин" if lang == "ru" else "min"
    text = (
        f"{t('cab_title', lang)}\n━━━━━━━━━━━━━━━━━━━━\n"
        f"{em.emoji('USERS')} {t('cab_name', lang)}: <b>{name}</b>\n"
        f"📞 {t('cab_phone', lang)}: <code>{phone}</code>\n"
        f"@ Username: <b>{uname}</b>\n\n"
        f"{em.emoji('STATS')} <b>{t('cab_stats', lang)}:</b>\n"
        f"{em.emoji('OK')} {t('cab_today', lang)}: <b>{total_today}</b>\n"
        f"🔄 {t('cab_total', lang)}: <b>{total_sent}</b>\n"
        f"{em.emoji('GROUP')} {t('p_groups', lang)}: <b>{total_groups}</b>\n"
        f"{em.emoji('USERS')} {t('cab_profiles', lang)}: <b>{len(accounts)}</b>\n\n"
        f"⭐ {t('cab_tarif', lang)}: <b>{t('cab_pro_yes', lang) if is_prem else t('cab_free', lang)}</b>\n"
        f"{em.emoji('CLOCK')} {t('p_interval', lang)}: <b>{interval} {unit}</b>"
    )
    await send_message(message.from_user.id, text,
                       reply_markup=menus.cabinet_kb(first["id"] if first else 0, lang))


# ═══════════════════════════════════════════════════════════════════
# 8. SOZLAMALAR (reply keyboard)
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "btn_settings"))
async def m_settings(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    text = f"{t('set_title', lang)}\n\n{t('set_q', lang)}\n\n{t('set_note', lang)}"
    await send_message(message.from_user.id, text, reply_markup=reply.settings_reply(lang))


@router.message(lambda m: _is_btn(m.text, "s_interval"))
async def m_set_interval(message: Message, state: FSMContext):
    await m_interval(message, state)


@router.message(lambda m: _is_btn(m.text, "s_dm"))
async def m_set_dm(message: Message, state: FSMContext):
    # DM Javob menyusi (Image 9)
    await state.clear()
    lang = await get_lang(message.from_user.id)
    account = await _first_account(message.from_user.id)
    if not account:
        await send_message(message.from_user.id, t("no_account", lang))
        return
    r = await db.get_dm_reply(account["id"])
    status = t("st_running", lang) if r["is_enabled"] else t("st_stopped", lang)
    msg = t("msg_set", lang) if r["reply_text"] else t("msg_notset", lang)
    # Avval menyu sarlavhasi
    await send_message(message.from_user.id, f"{em.emoji('CHAT')} <b>{t('dm_menu_title', lang)}</b>")
    # Keyin tafsilot + reply keyboard
    text = f"{em.emoji('CHAT')} <b>{t('dm_title', lang)}</b>\n\n" + t("dm_desc", lang, status=status, msg=msg)
    await send_message(message.from_user.id, text, reply_markup=reply.dm_reply_keyboard(lang))


@router.message(lambda m: _is_btn(m.text, "s_autosub"))
async def m_set_autosub(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    await send_message(message.from_user.id,
        f"{em.emoji('REFRESH')} <b>{t('s_autosub', lang)}</b>\n\n{t('soon', lang)}")


# ═══════════════════════════════════════════════════════════════════
# 9. KALENDAR
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "btn_calendar"))
async def m_calendar(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    await send_message(message.from_user.id,
        f"{t('cal_title', lang)}\n\n{t('cal_soon', lang)}")


# ═══════════════════════════════════════════════════════════════════
# 10. FOYDALI FUNKSIYALAR
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "btn_tools"))
async def m_tools(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    await send_message(message.from_user.id,
        f"{t('tools_title', lang)}\n\n{t('soon', lang)}")


# ═══════════════════════════════════════════════════════════════════
# 11. STATISTIKA (admin tavsif kirita oladi)
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "btn_stats"))
async def m_stats(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    accounts = await db.get_accounts(message.from_user.id)
    # Admin tomonidan kiritilgan tavsif
    desc = await db.get_setting(f"stats_desc_{lang}", "") or await db.get_setting("stats_desc_uz", "")
    text = f"{t('stat_title', lang)}\n━━━━━━━━━━━━━━━━━━━━\n"
    if desc:
        text += f"{desc}\n━━━━━━━━━━━━━━━━━━━━\n"
    if not accounts:
        text += t("stat_empty", lang)
    else:
        for a in accounts:
            st = await db.get_stats(a["id"])
            gc = await db.count_groups(a["id"])
            name = a["account_name"] or a["phone"]
            text += (f"\n{em.emoji('USER')} <b>{name}</b>\n"
                     f"   {em.emoji('GROUP')} {t('p_groups', lang)}: <b>{gc}</b>\n"
                     f"   {em.emoji('OK')} {t('cab_total', lang)}: <b>{st['sent']}</b>\n"
                     f"   📅 {t('cab_today', lang)}: <b>{st['today']}</b>\n")
    await send_message(message.from_user.id, text, reply_markup=menus.close_kb(lang))


# ═══════════════════════════════════════════════════════════════════
# 12. YORDAM (kanal/chat/admin + Murojat)
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "btn_help"))
async def m_help(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    channel = await db.get_setting("help_channel", "@autoxabar_news")
    chat = await db.get_setting("help_chat", "@autohabar_chat")
    admin = await db.get_setting("help_admin", f"@{config.admin_username}")
    text = (
        f"{t('help_title', lang)}\n━━━━━━━━━━━━━━━━━━━━\n"
        f"{em.emoji('CHAT')} {t('help_channel', lang)}: {channel}\n"
        f"{em.emoji('GROUP')} {t('help_chat', lang)}: {chat}\n"
        f"{em.emoji('USER')} {t('help_admin', lang)}: {admin}\n\n"
        f"{t('help_contact', lang)}"
    )
    await send_message(message.from_user.id, text, reply_markup=menus.help_kb(lang))


# ═══════════════════════════════════════════════════════════════════
# 13. QO'LLANMA (admin kiritadi)
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "btn_guide"))
async def m_guide(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    guide = await db.get_setting(f"guide_{lang}", "") or await db.get_setting("guide_uz", "")
    text = f"{t('guide_title', lang)}\n━━━━━━━━━━━━━━━━━━━━\n\n"
    text += guide if guide else t("guide_empty", lang)
    await send_message(message.from_user.id, text, reply_markup=menus.close_kb(lang))


# ═══════════════════════════════════════════════════════════════════
# 14. AUTOREPLY (reply keyboard — Image 12)
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "btn_autoreply"))
async def m_autoreply(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    account = await _first_account(message.from_user.id)
    if not account:
        await send_message(message.from_user.id, t("no_account", lang))
        return
    gr = await db.get_group_reply(account["id"])
    import json
    groups = json.loads(gr["groups_json"] or "[]")
    status = t("st_running", lang) if gr["is_enabled"] else t("st_stopped", lang)
    msg = t("msg_set", lang) if gr["reply_text"] else t("msg_notset", lang)
    text = f"{em.emoji('CHAT')} <b>{t('ar_title', lang)}</b>\n\n" + t("ar_desc", lang, status=status, msg=msg, n=len(groups))
    await send_message(message.from_user.id, text, reply_markup=reply.autoreply_keyboard(lang))


# ═══════════════════════════════════════════════════════════════════
# HOME / ORQAGA / YOPISH
# ═══════════════════════════════════════════════════════════════════
@router.message(lambda m: _is_btn(m.text, "back") or _is_btn(m.text, "home"))
async def m_home(message: Message, state: FSMContext):
    await state.clear()
    from app.handlers.start import show_main_menu
    await show_main_menu(message.from_user.id)


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
    lang = await get_lang(call.from_user.id)
    from app.userbot import login
    await login.cancel_login(call.from_user.id)
    accounts = await db.get_accounts(call.from_user.id)
    body = t("prof_count", lang, n=len(accounts)) if accounts else t("prof_none", lang)
    await edit_message(call.message.chat.id, call.message.message_id,
                       f"{t('prof_title', lang)}\n\n{body}",
                       reply_markup=menus.accounts_menu(accounts, lang))
    await answer_callback(call.id)
