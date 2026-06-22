"""
Barcha inline klaviaturalar — Elder Stars uslubida:
premium emoji (icon_custom_emoji_id) + rangli tugmalar (style).
"""
from aiogram.types import InlineKeyboardMarkup

from app.keyboards.builder import btn, kb
from app import emoji as em


# ═══════════════════════════════════════════════════════════════════
# ASOSIY MENYU
# ═══════════════════════════════════════════════════════════════════

def main_menu() -> InlineKeyboardMarkup:
    return kb([
        [btn("Autohabar yuborish", "autosend_menu", emoji=em.E_ROCKET, style="success"),
         btn("Autoreply", "autoreply_menu", emoji=em.E_CHAT, style="success")],
        [btn("Habar matni", "set_message", emoji=em.E_EDIT),
         btn("Interval", "set_interval", emoji=em.E_CLOCK)],
        [btn("Guruhlarni sozlash", "groups_menu", emoji=em.E_GROUP),
         btn("Akkauntlar", "accounts_menu", emoji=em.E_USER)],
        [btn("Statistika", "stats", emoji=em.E_STAR, style="primary"),
         btn("Sozlamalar", "settings", emoji=em.E_GEAR)],
        [btn("Yordam", "help", emoji=em.E_INFO)],
    ])


def back_main() -> InlineKeyboardMarkup:
    return kb([[btn("Bosh menyu", "back_main", emoji=em.E_BACK, style="primary")]])


# ═══════════════════════════════════════════════════════════════════
# AKKAUNT ULASH
# ═══════════════════════════════════════════════════════════════════

def accounts_menu(accounts: list) -> InlineKeyboardMarkup:
    rows = []
    for a in accounts:
        status = "🟢" if a["is_active"] else "🔴"
        name = a["account_name"] or a["phone"] or f"#{a['id']}"
        rows.append([btn(f"{status} {name}", f"account_{a['id']}", emoji=em.E_USER)])
    rows.append([btn("➕ Akkaunt qo'shish", "add_account", style="success")])
    rows.append([btn("Orqaga", "back_main", emoji=em.E_BACK)])
    return kb(rows)


def link_method() -> InlineKeyboardMarkup:
    """QR yoki SMS tanlash."""
    return kb([
        [btn("QR kod orqali", "link_qr", emoji=em.E_QR, style="primary")],
        [btn("SMS (telefon) orqali", "link_sms", emoji=em.E_PHONE)],
        [btn("Bekor qilish", "accounts_menu", emoji=em.E_BACK, style="danger")],
    ])


def qr_waiting_kb() -> InlineKeyboardMarkup:
    return kb([
        [btn("🔄 Yangilash", "link_qr")],
        [btn("SMS orqali ulash", "link_sms", emoji=em.E_PHONE)],
        [btn("Bekor qilish", "accounts_menu", emoji=em.E_BACK, style="danger")],
    ])


def cancel_link_kb() -> InlineKeyboardMarkup:
    return kb([[btn("Bekor qilish", "accounts_menu", emoji=em.E_BACK, style="danger")]])


def account_actions(account_id: int, is_running: bool) -> InlineKeyboardMarkup:
    """Bitta akkaunt boshqaruvi."""
    if is_running:
        toggle = btn("⏹ To'xtatish", f"stop_{account_id}", style="danger")
    else:
        toggle = btn("▶️ Ishga tushurish", f"start_{account_id}", style="success")
    return kb([
        [toggle],
        [btn("Guruhlar", f"acc_groups_{account_id}", emoji=em.E_GROUP),
         btn("Statistika", f"acc_stats_{account_id}", emoji=em.E_STAR)],
        [btn("Habar matni", f"acc_msg_{account_id}", emoji=em.E_EDIT),
         btn("Interval", f"acc_int_{account_id}", emoji=em.E_CLOCK)],
        [btn("Autoreply", f"acc_reply_{account_id}", emoji=em.E_CHAT)],
        [btn("🗑 Akkauntni o'chirish", f"del_acc_{account_id}", style="danger")],
        [btn("Orqaga", "accounts_menu", emoji=em.E_BACK)],
    ])


# ═══════════════════════════════════════════════════════════════════
# INTERVAL
# ═══════════════════════════════════════════════════════════════════

def interval_kb(account_id: int, current: int) -> InlineKeyboardMarkup:
    options = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 30, 60, 90, 120, 180]
    rows = []
    row = []
    for opt in options:
        label = f"{opt}daq" if opt < 60 else f"{opt//60} soat"
        if opt == current:
            label = f"✅ {label}"
        row.append(btn(label, f"setint_{account_id}_{opt}",
                       style="success" if opt == current else ""))
        if len(row) == 5:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([btn("Qo'lda kiritish", f"int_manual_{account_id}", emoji=em.E_EDIT, style="primary")])
    rows.append([btn("Orqaga", f"account_{account_id}", emoji=em.E_BACK)])
    return kb(rows)


# ═══════════════════════════════════════════════════════════════════
# GURUHLAR
# ═══════════════════════════════════════════════════════════════════

def groups_kb(account_id: int, groups: list, page: int = 0, per_page: int = 8) -> InlineKeyboardMarkup:
    rows = []
    start = page * per_page
    chunk = groups[start:start + per_page]
    for g in chunk:
        mark = "✅" if g["is_enabled"] else "⬜"
        title = (g["title"][:28] + "…") if len(g["title"]) > 28 else g["title"]
        rows.append([btn(f"{mark} {title}", f"togg_{account_id}_{g['id']}")])

    # Sahifalash
    nav = []
    if page > 0:
        nav.append(btn("◀️", f"gpage_{account_id}_{page-1}"))
    if start + per_page < len(groups):
        nav.append(btn("▶️", f"gpage_{account_id}_{page+1}"))
    if nav:
        rows.append(nav)

    rows.append([btn("🔄 Guruhlarni yangilash", f"refresh_groups_{account_id}", style="primary")])
    rows.append([btn("Orqaga", f"account_{account_id}", emoji=em.E_BACK)])
    return kb(rows)


# ═══════════════════════════════════════════════════════════════════
# AUTOREPLY
# ═══════════════════════════════════════════════════════════════════

def autoreply_kb(account_id: int, enabled: bool) -> InlineKeyboardMarkup:
    if enabled:
        toggle = btn("🔴 O'chirish", f"reply_off_{account_id}", style="danger")
    else:
        toggle = btn("🟢 Yoqish", f"reply_on_{account_id}", style="success")
    return kb([
        [toggle],
        [btn("Javob matnini o'zgartirish", f"reply_text_{account_id}", emoji=em.E_EDIT)],
        [btn("Orqaga", f"account_{account_id}", emoji=em.E_BACK)],
    ])


# ═══════════════════════════════════════════════════════════════════
# ADMIN
# ═══════════════════════════════════════════════════════════════════

def admin_menu() -> InlineKeyboardMarkup:
    return kb([
        [btn("Statistika", "adm_stats", emoji=em.E_STAR, style="primary"),
         btn("Foydalanuvchilar", "adm_users", emoji=em.E_USER)],
        [btn("Premium berish", "adm_give_premium", emoji=em.E_OK, style="success"),
         btn("Premium olish", "adm_take_premium", emoji=em.E_WARN, style="danger")],
        [btn("Xabar yuborish (broadcast)", "adm_broadcast", emoji=em.E_ROCKET)],
        [btn("Bosh menyu", "back_main", emoji=em.E_BACK)],
    ])


def admin_back() -> InlineKeyboardMarkup:
    return kb([[btn("Orqaga", "adm_main", emoji=em.E_BACK)]])
