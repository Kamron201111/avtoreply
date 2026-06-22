"""
Pastdagi tugmalar (ReplyKeyboard) — asosiy menyu.
Raw API orqali yuboriladi, shuning uchun premium emoji (icon) + style ishlaydi.
"""
from app.keyboards.builder import reply_kb, rbtn
from app import emoji as em


# ─── Tugma matnlari (handlerda solishtirish uchun) ──────────────────
# Eslatma: F.text.contains() bilan ushlash uchun matnlarda kalit so'z bo'ladi
BTN_AUTOSEND  = "Autohabar yuborish"
BTN_MESSAGE   = "Habar matni"
BTN_INTERVAL  = "Interval"
BTN_GROUPS    = "Guruhlarni sozlash"
BTN_PROFILES  = "Profillar"
BTN_PRO       = "Pro tarif"
BTN_CABINET   = "Kabinet"
BTN_SETTINGS  = "Sozlamalar"
BTN_CALENDAR  = "Kalendar"
BTN_TOOLS     = "Foydali funksiyalar"
BTN_STATS     = "Statistika"
BTN_HELP      = "Yordam"
BTN_GUIDE     = "Qo'llanma"
BTN_AUTOREPLY = "Autoreply"


def main_menu() -> dict:
    """Asosiy menyu (raw reply keyboard, premium emoji + rang)."""
    return reply_kb([
        [rbtn(f"🚀 {BTN_AUTOSEND}", icon="ROCKET", style="success"),
         rbtn(f"📝 {BTN_MESSAGE}", icon="EDIT", style="success")],
        [rbtn(f"⏰ {BTN_INTERVAL}", icon="CLOCK", style="primary"),
         rbtn(f"💬 {BTN_GROUPS}", icon="GROUP", style="primary")],
        [rbtn(f"👥 {BTN_PROFILES}", icon="USERS", style="danger"),
         rbtn(f"👑 {BTN_PRO}", icon="CROWN", style="danger")],
        [rbtn(f"👤 {BTN_CABINET}", icon="USER", style="primary"),
         rbtn(f"⚙️ {BTN_SETTINGS}", icon="GEAR", style="primary")],
        [rbtn(f"📅 {BTN_CALENDAR}", icon="CALENDAR", style="primary"),
         rbtn(f"🔧 {BTN_TOOLS}", icon="TOOLS")],
        [rbtn(f"📊 {BTN_STATS}", icon="STATS", style="success"),
         rbtn(f"🎧 {BTN_HELP}", icon="INFO", style="success")],
        [rbtn(f"📕 {BTN_GUIDE}", icon="BOOK", style="danger"),
         rbtn(f"🔄 {BTN_AUTOREPLY}", icon="REPLY")],
    ], placeholder="Tugmani tanlang...")
