"""
Barcha inline klaviaturalar (raw dict — style + premium emoji bilan).
Skrinshотlardagi dizaynга aynan mos.
"""
from app.keyboards.builder import btn, inline_kb


# ═══════════════════════════════════════════════════════════════════
# AKKAUNT (PROFIL) BOSHQARUV — Image 1
# ═══════════════════════════════════════════════════════════════════

def account_panel(account_id: int, is_running: bool, mention_on: bool) -> dict:
    """Boshqaruv panel (Image 1)."""
    if is_running:
        toggle = btn("To'xtatish", cb=f"stop_{account_id}", icon="STOP", style="danger")
    else:
        toggle = btn("Ishga tushurish", cb=f"start_{account_id}", icon="PLAY", style="success")

    mention_txt = "Yoqilgan" if mention_on else "O'chiq"
    return inline_kb([
        [toggle,
         btn("Statistika", cb=f"acc_stats_{account_id}", icon="STATS", style="danger")],
        [btn("Avto-o'chirish taymeri", cb=f"acc_timer_{account_id}", icon="TIMER", style="primary"),
         btn(f"Mention: {mention_txt} 🔴",
             cb=f"acc_mention_{account_id}", icon="MENTION", style="primary")],
        [btn("Yopish", cb="close_msg", icon="BACK", style="danger")],
    ])


# ═══════════════════════════════════════════════════════════════════
# HABAR MATNI — Image 2
# ═══════════════════════════════════════════════════════════════════

def message_type_kb(account_id: int) -> dict:
    """Xabar turini tanlash (Image 2)."""
    return inline_kb([
        [btn("Matn", cb=f"mtype_text_{account_id}", icon="EDIT", style="primary")],
        [btn("Rasm+matn", cb=f"mtype_photo_{account_id}", icon="CAMERA", style="primary")],
        [btn("Forward 🔒", cb=f"mtype_fwd_{account_id}", icon="REPLY", style="danger")],
        [btn("Tugmali habar", cb=f"mtype_btn_{account_id}", icon="GEAR", style="success")],
        [btn("Turli habarlar 🔒", cb=f"mtype_multi_{account_id}", icon="CHAT", style="danger")],
        [btn("Orqaga", cb=f"account_{account_id}", icon="BACK", style="danger")],
    ])


# ═══════════════════════════════════════════════════════════════════
# INTERVAL — Image 3
# ═══════════════════════════════════════════════════════════════════

def interval_kb(account_id: int, current: int) -> dict:
    """Interval tanlash (Image 3)."""
    presets = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 30, 60, 90, 120, 180]
    rows = []
    row = []
    for opt in presets:
        if opt < 60:
            label = f"{opt}daq"
        elif opt == 60:
            label = "1 soat"
        elif opt == 90:
            label = "1.5 soat"
        else:
            label = f"{opt//60} soat"
        if opt == current:
            label = f"✅ {label}"
            b = btn(label, cb=f"setint_{account_id}_{opt}", style="success")
        else:
            b = btn(label, cb=f"setint_{account_id}_{opt}", style="danger")
        row.append(b)
        if len(row) == 5:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([btn("Interval nima", cb="int_what", icon="INFO", style="primary")])
    rows.append([btn("Qo'lda kiritish", cb=f"int_manual_{account_id}", icon="EDIT", style="success")])
    rows.append([btn("Orqaga", cb=f"account_{account_id}", icon="BACK", style="danger")])
    return inline_kb(rows)


# ═══════════════════════════════════════════════════════════════════
# GURUHLARNI SOZLASH — Image 4
# ═══════════════════════════════════════════════════════════════════

def groups_choice_kb(account_id: int) -> dict:
    """Hamma / o'zim tanlayman (Image 4)."""
    return inline_kb([
        [btn("Hamma guruhlarga", cb=f"grp_all_{account_id}", icon="CHECK", style="primary")],
        [btn("O'zim tanlayman", cb=f"grp_pick_{account_id}", icon="EDIT", style="primary")],
        [btn("Orqaga", cb=f"account_{account_id}", icon="BACK", style="danger")],
    ])


def groups_list_kb(account_id: int, groups: list, page: int = 0, per: int = 8) -> dict:
    """Guruhlar ro'yxati (yoqish/o'chirish)."""
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
    rows.append([btn("🔄 Yangilash", cb=f"grefresh_{account_id}", icon="REFRESH", style="primary")])
    rows.append([btn("Orqaga", cb=f"grp_back_{account_id}", icon="BACK", style="danger")])
    return inline_kb(rows)


# ═══════════════════════════════════════════════════════════════════
# KABINET — Image 5
# ═══════════════════════════════════════════════════════════════════

def cabinet_kb(account_id: int = 0) -> dict:
    """Kabinet (Image 5)."""
    rows = []
    if account_id:
        rows.append([btn("Profilni uzish", cb=f"del_acc_{account_id}", icon="WARN", style="danger")])
    rows.append([btn("Yopish", cb="close_msg", icon="CROSS", style="danger")])
    return inline_kb(rows)


# ═══════════════════════════════════════════════════════════════════
# PROFILLAR (akkauntlar ro'yxati)
# ═══════════════════════════════════════════════════════════════════

def accounts_menu(accounts: list) -> dict:
    rows = []
    for a in accounts:
        status = "🟢" if a["is_active"] else "🔴"
        name = a["account_name"] or a["phone"] or f"#{a['id']}"
        rows.append([btn(f"{status} {name}", cb=f"account_{a['id']}", icon="USER")])
    rows.append([btn("➕ Akkaunt qo'shish", cb="add_account", icon="OK", style="success")])
    rows.append([btn("Yopish", cb="close_msg", icon="BACK", style="danger")])
    return inline_kb(rows)


def link_method() -> dict:
    """QR yoki SMS tanlash."""
    return inline_kb([
        [btn("QR kod orqali", cb="link_qr", icon="QR", style="primary")],
        [btn("SMS (telefon) orqali", cb="link_sms", icon="PHONE", style="primary")],
        [btn("Bekor qilish", cb="profiles_back", icon="BACK", style="danger")],
    ])


def qr_waiting_kb() -> dict:
    return inline_kb([
        [btn("🔄 Yangilash", cb="link_qr", icon="REFRESH", style="primary")],
        [btn("SMS orqali", cb="link_sms", icon="PHONE")],
        [btn("Bekor qilish", cb="profiles_back", icon="BACK", style="danger")],
    ])


def cancel_link_kb() -> dict:
    return inline_kb([[btn("Bekor qilish", cb="profiles_back", icon="BACK", style="danger")]])


# ═══════════════════════════════════════════════════════════════════
# SOZLAMALAR (reply keyboard) — Image 6
# ═══════════════════════════════════════════════════════════════════

def settings_reply() -> dict:
    """Umumiy sozlamalar reply keyboard (Image 6)."""
    from app.keyboards.builder import reply_kb, rbtn
    return reply_kb([
        [rbtn("⏰ Har bir habar oraligi", icon="CLOCK", style="primary"),
         rbtn("DM javob", icon="CHAT", style="primary")],
        [rbtn("🔄 Avtomatik obuna", icon="REFRESH", style="primary")],
        [rbtn("⬅️ Orqaga", icon="BACK", style="danger")],
    ], placeholder="Sozlamani tanlang...")


# ═══════════════════════════════════════════════════════════════════
# PRO TARIF
# ═══════════════════════════════════════════════════════════════════

def pro_kb(is_premium: bool) -> dict:
    rows = []
    if not is_premium:
        rows.append([btn("💳 Karta orqali", cb="pro_card", icon="CARD", style="success")])
        rows.append([btn("⭐️ Stars orqali", cb="pro_stars", icon="STAR", style="primary")])
    rows.append([btn("🎁 Boshqaga sovg'a qilish", cb="pro_gift", icon="GIFT", style="primary")])
    rows.append([btn("Yopish", cb="close_msg", icon="BACK", style="danger")])
    return inline_kb(rows)


def pro_pay_kb(method: str) -> dict:
    """To'lov tasdiqlash."""
    return inline_kb([
        [btn("✅ To'ladim", cb=f"paid_{method}", icon="OK", style="success")],
        [btn("Bekor qilish", cb="pro_back", icon="BACK", style="danger")],
    ])


# ═══════════════════════════════════════════════════════════════════
# AUTOREPLY
# ═══════════════════════════════════════════════════════════════════

def autoreply_kb(account_id: int, enabled: bool) -> dict:
    if enabled:
        toggle = btn("🔴 O'chirish", cb=f"reply_off_{account_id}", icon="STOP", style="danger")
    else:
        toggle = btn("🟢 Yoqish", cb=f"reply_on_{account_id}", icon="OK", style="success")
    return inline_kb([
        [toggle],
        [btn("Javob matni", cb=f"reply_text_{account_id}", icon="EDIT", style="primary")],
        [btn("Orqaga", cb=f"account_{account_id}", icon="BACK", style="danger")],
    ])


# ═══════════════════════════════════════════════════════════════════
# ADMIN
# ═══════════════════════════════════════════════════════════════════

def admin_menu() -> dict:
    return inline_kb([
        [btn("Statistika", cb="adm_stats", icon="STATS", style="primary"),
         btn("Foydalanuvchilar", cb="adm_users", icon="USERS")],
        [btn("Premium berish", cb="adm_give_premium", icon="OK", style="success"),
         btn("Premium olish", cb="adm_take_premium", icon="WARN", style="danger")],
        [btn("Pro narxlari", cb="adm_prices", icon="MONEY", style="primary"),
         btn("Karta raqami", cb="adm_card", icon="CARD", style="primary")],
        [btn("Broadcast", cb="adm_broadcast", icon="ROCKET", style="success")],
        [btn("Yopish", cb="close_msg", icon="BACK", style="danger")],
    ])


def admin_back() -> dict:
    return inline_kb([[btn("Orqaga", cb="adm_main", icon="BACK", style="danger")]])


# ─── Umumiy yordamchi ───────────────────────────────────────────────

def close_kb() -> dict:
    return inline_kb([[btn("Yopish", cb="close_msg", icon="BACK", style="danger")]])


def back_main() -> dict:
    return inline_kb([[btn("Yopish", cb="close_msg", icon="BACK", style="danger")]])


# ─── Yordamchilar ───────────────────────────────────────────────────
def inline_back(cb: str) -> dict:
    """Bitta 'Orqaga' tugmasi."""
    return inline_kb([[btn("Orqaga", cb=cb, icon="BACK", style="danger")]])
