"""
Barcha inline klaviaturalar — 3 tilli, raw dict (style + premium emoji).
"""
from app.keyboards.builder import btn, inline_kb
from app.i18n import t


# ═══ AKKAUNT PANEL (Image 2) ═══
def account_panel(account_id, is_running, mention_on, lang="uz"):
    if is_running:
        toggle = btn(t("btn_stop", lang), cb=f"stop_{account_id}", icon="STOP", style="danger")
    else:
        toggle = btn(t("btn_start", lang), cb=f"start_{account_id}", icon="PLAY", style="success")
    mention_txt = t("on", lang) if mention_on else t("off", lang)
    return inline_kb([
        [toggle, btn(t("btn_p_stats", lang), cb=f"acc_stats_{account_id}", icon="STATS", style="danger")],
        [btn(t("btn_autodel", lang), cb=f"acc_timer_{account_id}", icon="TIMER", style="primary"),
         btn(f"{t('p_mention', lang)}: {mention_txt} 🔴", cb=f"acc_mention_{account_id}", icon="MENTION", style="primary")],
        [btn(t("close", lang), cb="close_msg", icon="BACK", style="danger")],
    ])


# ═══ HABAR MATNI (Image 5) ═══
def message_type_kb(account_id, lang="uz"):
    return inline_kb([
        [btn(t("b_text", lang), cb=f"mtype_text_{account_id}", icon="EDIT", style="primary")],
        [btn(t("b_photo", lang), cb=f"mtype_photo_{account_id}", icon="CAMERA", style="primary")],
        [btn(t("b_fwd", lang), cb=f"mtype_fwd_{account_id}", icon="REPLY", style="danger")],
        [btn(t("b_btnmsg", lang), cb=f"mtype_btn_{account_id}", icon="GEAR", style="success")],
        [btn(t("b_multi", lang), cb=f"mtype_multi_{account_id}", icon="CHAT", style="danger")],
        [btn(t("back", lang), cb=f"account_{account_id}", icon="BACK", style="danger")],
    ])


# ═══ INTERVAL (Image 3/8) — minutlarda ═══
def interval_kb(account_id, current, lang="uz"):
    presets = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 30, 60, 90, 120, 180]
    rows, row = [], []
    for opt in presets:
        if opt < 60:
            label = f"{opt}daq" if lang == "uz" else f"{opt}мин" if lang == "ru" else f"{opt}m"
        else:
            h = opt // 60
            label = (f"{h} soat" if lang == "uz" else f"{h} ч" if lang == "ru" else f"{h}h")
            if opt == 90:
                label = "1.5 soat" if lang == "uz" else "1.5 ч" if lang == "ru" else "1.5h"
        style = "success" if opt == current else "danger"
        if opt == current:
            label = f"✅ {label}"
        row.append(btn(label, cb=f"setint_{account_id}_{opt}", style=style))
        if len(row) == 5:
            rows.append(row); row = []
    if row:
        rows.append(row)
    rows.append([btn(t("int_what_btn", lang), cb="int_what", icon="INFO", style="primary")])
    rows.append([btn(t("int_manual", lang), cb=f"int_manual_{account_id}", icon="EDIT", style="success")])
    rows.append([btn(t("back", lang), cb=f"account_{account_id}", icon="BACK", style="danger")])
    return inline_kb(rows)


# ═══ GURUHLAR (Image 6) ═══
def groups_choice_kb(account_id, lang="uz"):
    return inline_kb([
        [btn(t("b_grp_all", lang), cb=f"grp_all_{account_id}", icon="CHECK", style="primary")],
        [btn(t("b_grp_pick", lang), cb=f"grp_pick_{account_id}", icon="EDIT", style="primary")],
        [btn(t("back", lang), cb=f"account_{account_id}", icon="BACK", style="danger")],
    ])


def groups_pick_kb(account_id, lang="uz"):
    """O'zim tanlayman bosilganda — Ro'yxatlar/Qo'shish/O'chirish (Image 6)."""
    return inline_kb([
        [btn(t("b_grp_lists", lang), cb=f"glist_{account_id}", icon="STATS", style="primary"),
         btn(t("b_grp_add", lang), cb=f"gadd_{account_id}", icon="OK", style="success"),
         btn(t("b_grp_del", lang), cb=f"gdel_{account_id}", icon="CROSS", style="danger")],
        [btn(t("back", lang), cb=f"grp_back_{account_id}", icon="BACK", style="danger")],
    ])


def groups_list_kb(account_id, groups, page=0, per=8, lang="uz"):
    rows = []
    start = page * per
    for g in groups[start:start + per]:
        mark = "✅" if g["is_enabled"] else "⬜"
        title = (g["title"][:30] + "…") if len(g["title"]) > 30 else g["title"]
        rows.append([btn(f"{mark} {title}", cb=f"gtog_{account_id}_{g['id']}")])
    nav = []
    if page > 0:
        nav.append(btn("◀️", cb=f"gpg_{account_id}_{page-1}"))
    if start + per < len(groups):
        nav.append(btn("▶️", cb=f"gpg_{account_id}_{page+1}"))
    if nav:
        rows.append(nav)
    rows.append([btn(t("qr_refresh", lang), cb=f"grefresh_{account_id}", icon="REFRESH", style="primary")])
    rows.append([btn(t("back", lang), cb=f"gpick_back_{account_id}", icon="BACK", style="danger")])
    return inline_kb(rows)


# ═══ KABINET (Image 5/10) ═══
def cabinet_kb(account_id=0, lang="uz"):
    rows = []
    if account_id:
        rows.append([btn(t("b_del_acc", lang), cb=f"del_acc_{account_id}", icon="WARN", style="danger")])
    rows.append([btn(t("close", lang), cb="close_msg", icon="CROSS", style="danger")])
    return inline_kb(rows)


# ═══ PROFILLAR ═══
def accounts_menu(accounts, lang="uz"):
    rows = []
    for a in accounts:
        status = "🟢" if a["is_active"] else "🔴"
        name = a["account_name"] or a["phone"] or f"#{a['id']}"
        rows.append([btn(f"{status} {name}", cb=f"account_{a['id']}", icon="USER")])
    rows.append([btn(t("b_add_acc", lang), cb="add_account", icon="OK", style="success")])
    rows.append([btn(t("close", lang), cb="close_msg", icon="BACK", style="danger")])
    return inline_kb(rows)


def link_method(lang="uz"):
    return inline_kb([
        [btn(t("b_link_qr", lang), cb="link_qr", icon="QR", style="primary")],
        [btn(t("b_link_sms", lang), cb="link_sms", icon="PHONE", style="primary")],
        [btn(t("cancel", lang), cb="profiles_back", icon="BACK", style="danger")],
    ])


def qr_waiting_kb(lang="uz"):
    return inline_kb([
        [btn(t("qr_refresh", lang), cb="link_qr", icon="REFRESH", style="primary")],
        [btn(t("b_link_sms", lang), cb="link_sms", icon="PHONE")],
        [btn(t("cancel", lang), cb="profiles_back", icon="BACK", style="danger")],
    ])


def cancel_link_kb(lang="uz"):
    return inline_kb([[btn(t("cancel", lang), cb="profiles_back", icon="BACK", style="danger")]])


# ═══ PRO ═══
def pro_kb(is_premium, lang="uz"):
    rows = []
    if not is_premium:
        rows.append([btn(t("b_pro_stars", lang), cb="pro_stars", icon="STAR", style="success")])
        rows.append([btn(t("b_pro_card", lang), cb="pro_card", icon="CARD", style="primary")])
    rows.append([btn(t("b_pro_gift", lang), cb="pro_gift", icon="GIFT", style="primary")])
    rows.append([btn(t("b_pro_admin", lang), cb="contact_admin", icon="USER")])
    rows.append([btn(t("close", lang), cb="close_msg", icon="BACK", style="danger")])
    return inline_kb(rows)


def pro_pay_kb(method, lang="uz"):
    return inline_kb([
        [btn(t("b_paid", lang), cb=f"paid_{method}", icon="OK", style="success")],
        [btn(t("cancel", lang), cb="pro_back", icon="BACK", style="danger")],
    ])


# ═══ YORDAM ═══
def help_kb(lang="uz"):
    return inline_kb([
        [btn(t("b_contact", lang), cb="contact_admin", icon="REPLY", style="success")],
        [btn(t("close", lang), cb="close_msg", icon="BACK", style="danger")],
    ])


# ═══ MENTION ogohlantirish ═══
def mention_warn_kb(account_id, lang="uz"):
    return inline_kb([
        [btn(t("yes_understand", lang), cb=f"mention_yes_{account_id}", icon="OK", style="danger")],
        [btn(t("back", lang), cb=f"account_{account_id}", icon="BACK", style="primary")],
    ])


# ═══ ADMIN ═══
def admin_menu(lang="uz"):
    return inline_kb([
        [btn("📊 Statistika", cb="adm_stats", icon="STATS", style="primary"),
         btn("👥 Foydalanuvchilar", cb="adm_users", icon="USERS")],
        [btn("👑 Premium berish", cb="adm_give_premium", icon="OK", style="success"),
         btn("🚫 Premium olish", cb="adm_take_premium", icon="WARN", style="danger")],
        [btn("💰 Pro narxlari", cb="adm_prices", icon="MONEY", style="primary"),
         btn("💳 Karta raqami", cb="adm_card", icon="CARD", style="primary")],
        [btn("📕 Qo'llanma matni", cb="adm_guide", icon="BOOK", style="success"),
         btn("📊 Statistika tavsifi", cb="adm_statsdesc", icon="STATS", style="success")],
        [btn("🎧 Yordam sozlash", cb="adm_help", icon="INFO", style="primary"),
         btn("📢 Majburiy obuna", cb="adm_channels", icon="CHAT", style="primary")],
        [btn("📨 Murojatlar", cb="adm_tickets", icon="REPLY", style="success"),
         btn("📣 Broadcast", cb="adm_broadcast", icon="ROCKET", style="success")],
        [btn(t("close", lang), cb="close_msg", icon="BACK", style="danger")],
    ])


def admin_back(lang="uz"):
    return inline_kb([[btn(t("back", lang), cb="adm_main", icon="BACK", style="danger")]])


# ═══ Yordamchilar ═══
def close_kb(lang="uz"):
    return inline_kb([[btn(t("close", lang), cb="close_msg", icon="BACK", style="danger")]])


def inline_back(cb, lang="uz"):
    return inline_kb([[btn(t("back", lang), cb=cb, icon="BACK", style="danger")]])


def autoreply_inline(account_id, enabled, lang="uz"):
    if enabled:
        toggle = btn("🔴 " + t("off", lang), cb=f"reply_off_{account_id}", icon="STOP", style="danger")
    else:
        toggle = btn("🟢 " + t("on", lang), cb=f"reply_on_{account_id}", icon="OK", style="success")
    return inline_kb([
        [toggle],
        [btn(t("dm_b_setmsg", lang), cb=f"reply_text_{account_id}", icon="EDIT", style="primary")],
        [btn(t("back", lang), cb=f"account_{account_id}", icon="BACK", style="danger")],
    ])
