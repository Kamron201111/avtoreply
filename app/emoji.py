"""
Premium emoji yordamchilari.

Bot Premium obunaga ega (27k+ oylik obunachi), shuning uchun xabar MATNIDA
premium emoji ishlatish mumkin: <tg-emoji emoji-id="...">😀</tg-emoji>

MUHIM:
  • Premium emoji faqat XABAR MATNIDA ishlaydi (HTML parse_mode bilan).
  • ReplyKeyboard TUGMALARIDA premium emoji BO'LMAYDI — u yerda oddiy emoji.
  • Agar bot Premium'ni yo'qotsa, USE_PREMIUM_EMOJI = False qiling.
"""

# Premium emoji yoqilganmi? (bot Premium obunaga ega bo'lsa True)
USE_PREMIUM_EMOJI = True

# ─── Premium Emoji ID lar (siz bergan ro'yxatdan tanlangan) ─────────
PREMIUM_IDS = {
    "wave":   "5816508088227730739",   # 👋
    "star":   "5895702479097564641",   # ⭐️
    "rocket": "5895720492190404869",   # 🚀
    "edit":   "5897737086710059363",   # 📝
    "clock":  "5816934234882839927",   # ⏰
    "chat":   "5985293048760766504",   # 💬
    "group":  "5933769822214034093",   # 💬 (guruh)
    "user":   "5897785405092138893",   # 👨‍💻
    "gear":   "5895592588064328942",   # ⚙️
    "info":   "5816742056571180106",   # ℹ️
    "ok":     "5895231943955451762",   # ✅
    "warn":   "5852487725051023314",   # ⛔
    "crown":  "5895709153476742796",   # 👑
    "phone":  "6037232942969786590",   # 📱
    "qr":     "6037193420680729470",   # 📱 (QR uchun)
    "key":    "5897604269141398480",   # 🔐
    "back":   "5985764515910784774",   # ⬅️
    "play":   "5895705279416241926",   # ▶️
    "shop":   "5895288113537748673",   # 🏪
    "calendar": "5895731156594200261", # 📷 (kalendar o'rniga)
    "tools":  "5895483165182529286",   # 🛡 (foydali funksiyalar)
    "book":   "5895583431194054511",   # 🌟 (qo'llanma)
    "stats":  "5852974147277164834",   # ⭐ (statistika)
}

# ─── Oddiy emoji (ReplyKeyboard tugmalari va fallback uchun) ────────
PLAIN = {
    "wave": "👋", "star": "⭐️", "rocket": "🚀", "edit": "📝",
    "clock": "🕐", "chat": "💬", "group": "💬", "user": "👤",
    "gear": "⚙️", "info": "ℹ️", "ok": "✅", "warn": "⛔",
    "crown": "👑", "phone": "📱", "qr": "📲", "key": "🔐",
    "back": "⬅️", "play": "▶️", "shop": "🏪", "calendar": "📅",
    "tools": "🔧", "book": "📕", "stats": "📊", "profile": "👥",
    "settings": "⚙️", "help": "🎧", "autoreply": "🔄",
}


def pe(name: str) -> str:
    """
    Premium emoji (xabar matni uchun). HTML parse_mode kerak.
    Premium o'chiq bo'lsa oddiy emoji qaytaradi.
    """
    plain = PLAIN.get(name, "•")
    if USE_PREMIUM_EMOJI and name in PREMIUM_IDS:
        return f'<tg-emoji emoji-id="{PREMIUM_IDS[name]}">{plain}</tg-emoji>'
    return plain


def oe(name: str) -> str:
    """Oddiy emoji (ReplyKeyboard tugmalari uchun)."""
    return PLAIN.get(name, "•")


# ─── Eski kod bilan moslik uchun (handlerlarda ishlatilgan) ────────
E_WAVE = "wave"
E_STAR = "star"
E_ROCKET = "rocket"
E_EDIT = "edit"
E_CLOCK = "clock"
E_CHAT = "chat"
E_GROUP = "group"
E_USER = "user"
E_GEAR = "gear"
E_INFO = "info"
E_OK = "ok"
E_WARN = "warn"
E_PHONE = "phone"
E_QR = "qr"
E_KEY = "key"
E_BACK = "back"
E_ID = "info"
E_MONEY = "star"


def tg_emoji(name_or_id: str, fallback: str = "") -> str:
    """Eski kod uchun — premium emoji qaytaradi (matn uchun)."""
    # Agar 'name' bo'lsa (E_* dan kelgan)
    if name_or_id in PREMIUM_IDS or name_or_id in PLAIN:
        return pe(name_or_id)
    # Agar to'g'ridan-to'g'ri ID bo'lsa
    if USE_PREMIUM_EMOJI and name_or_id.isdigit():
        return f'<tg-emoji emoji-id="{name_or_id}">{fallback}</tg-emoji>'
    return fallback if fallback else name_or_id


# Eski funksiyalar (matn uchun premium emoji)
def eW() -> str: return pe("wave")
def eST() -> str: return pe("star")
def eMN() -> str: return pe("star")
def eUS() -> str: return pe("user")
def eIN() -> str: return pe("info")
def eID() -> str: return pe("info")
def eWL() -> str: return pe("star")
def eOK() -> str: return pe("ok")
def eCL() -> str: return pe("clock")
def eWN() -> str: return pe("warn")
def eRK() -> str: return pe("rocket")
def eGR() -> str: return pe("group")
def eGE() -> str: return pe("gear")
def eQR() -> str: return pe("qr")
def ePH() -> str: return pe("phone")
