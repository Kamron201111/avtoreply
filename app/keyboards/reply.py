"""
Pastdagi tugmalar (ReplyKeyboard) — 3 tilli, premium emoji + rang.
Admin uchun oxirida «Admin panel» tugmasi qo'shiladi.
"""
from app.keyboards.builder import reply_kb, rbtn
from app.i18n import t, LANGS
from app.config import config

def _strip_emoji(text: str) -> str:
    """Matn boshidagi emoji va bo'shliqni olib tashlaydi (premium icon qoladi)."""
    # Birinchi bo'shliqdan keyingi qismni olamiz (emoji odatda birinchi "so'z")
    parts = text.split(" ", 1)
    if len(parts) == 2:
        first = parts[0]
        # Agar birinchi qism harf/raqam bo'lmasa (ya'ni emoji), olib tashlaymiz
        if first and not any(c.isalnum() for c in first):
            return parts[1]
    return text



def lang_kb() -> dict:
    """Til tanlash (inline)."""
    from app.keyboards.builder import btn, inline_kb
    return inline_kb([
        [btn("🇺🇿 O'zbekcha", cb="setlang_uz")],
        [btn("🇷🇺 Русский", cb="setlang_ru")],
        [btn("🇬🇧 English", cb="setlang_en")],
    ])


def main_menu(lang: str = "uz", is_admin: bool = False) -> dict:
    """Asosiy menyu (til bo'yicha + admin tugmasi)."""
    rows = [
        [rbtn(_strip_emoji(t("btn_autosend", lang)), icon="ROCKET", style="success"),
         rbtn(_strip_emoji(t("btn_message", lang)), icon="EDIT", style="success")],
        [rbtn(_strip_emoji(t("btn_interval", lang)), icon="CLOCK", style="primary"),
         rbtn(_strip_emoji(t("btn_groups", lang)), icon="GROUP", style="primary")],
        [rbtn(_strip_emoji(t("btn_profiles", lang)), icon="USERS", style="danger"),
         rbtn(_strip_emoji(t("btn_pro", lang)), icon="CROWN", style="danger")],
        [rbtn(_strip_emoji(t("btn_cabinet", lang)), icon="USER", style="primary"),
         rbtn(_strip_emoji(t("btn_settings", lang)), icon="GEAR", style="primary")],
        [rbtn(_strip_emoji(t("btn_stats", lang)), icon="STATS", style="success"),
         rbtn(_strip_emoji(t("btn_help", lang)), icon="INFO", style="success")],
        [rbtn(_strip_emoji(t("btn_guide", lang)), icon="BOOK", style="danger"),
         rbtn(_strip_emoji(t("btn_autoreply", lang)), icon="REPLY")],
    ]
    # Admin tugmasi — eng oxirida
    if is_admin:
        rows.append([rbtn(_strip_emoji(t("btn_admin", lang)), icon="GEAR", style="danger")])
    return reply_kb(rows, placeholder="Menu")


# ─── Sozlamalar reply keyboard ──────────────────────────────────────
def settings_reply(lang: str = "uz") -> dict:
    return reply_kb([
        [rbtn(t("s_interval", lang), icon="CLOCK", style="primary"),
         rbtn(t("s_dm", lang), icon="CHAT", style="primary")],
        [rbtn(t("s_autosub", lang), icon="REFRESH", style="primary")],
        [rbtn(t("back", lang), icon="BACK", style="danger")],
    ], placeholder="...")


# ─── DM Javob reply keyboard (Image 9) ──────────────────────────────
def dm_reply_keyboard(lang: str = "uz") -> dict:
    return reply_kb([
        [rbtn(t("dm_b_run", lang), icon="PLAY", style="success"),
         rbtn(t("dm_b_setmsg", lang), icon="EDIT", style="primary")],
        [rbtn(t("home", lang), icon="BACK", style="danger")],
    ], placeholder="...")


# ─── Autoreply reply keyboard (Image 12) ────────────────────────────
def autoreply_keyboard(lang: str = "uz") -> dict:
    return reply_kb([
        [rbtn(t("ar_run", lang), icon="PLAY", style="danger"),
         rbtn(t("ar_replymsg", lang), icon="EDIT", style="danger")],
        [rbtn(t("ar_replygrp", lang), icon="USERS", style="danger"),
         rbtn(t("ar_dontsend", lang), icon="CROSS", style="primary")],
        [rbtn(t("ar_settings", lang)),
         rbtn(t("home", lang), icon="BACK", style="danger")],
    ], placeholder="...")


# ─── ADMIN PANEL reply keyboard ─────────────────────────────────────
def admin_menu(lang: str = "uz") -> dict:
    """Admin panel — pastdagi tugmalar (reply keyboard)."""
    return reply_kb([
        [rbtn(_strip_emoji(t("adm_b_stats", lang)), icon="STATS", style="primary"),
         rbtn(_strip_emoji(t("adm_b_users", lang)), icon="USERS", style="primary")],
        [rbtn(_strip_emoji(t("adm_b_give", lang)), icon="CROWN", style="success"),
         rbtn(_strip_emoji(t("adm_b_take", lang)), icon="WARN", style="danger")],
        [rbtn(_strip_emoji(t("adm_b_prices", lang)), icon="MONEY", style="primary"),
         rbtn(_strip_emoji(t("adm_b_card", lang)), icon="CARD", style="primary")],
        [rbtn(_strip_emoji(t("adm_b_guide", lang)), icon="BOOK", style="success"),
         rbtn(_strip_emoji(t("adm_b_statsdesc", lang)), icon="STATS", style="success")],
        [rbtn(_strip_emoji(t("adm_b_help", lang)), icon="INFO", style="primary"),
         rbtn(_strip_emoji(t("adm_b_channels", lang)), icon="CHAT", style="primary")],
        [rbtn(_strip_emoji(t("adm_b_tickets", lang)), icon="REPLY", style="success"),
         rbtn(_strip_emoji(t("adm_b_broadcast", lang)), icon="ROCKET", style="success")],
        [rbtn(_strip_emoji(t("adm_b_exit", lang)), icon="BACK", style="danger")],
    ], placeholder="Admin")
