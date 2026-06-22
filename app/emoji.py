"""
Premium (custom) emoji katalogi.

Siz bergan haqiqiy emoji ID'lar. Bot Premium emoji huquqiga ega.

ISHLATISH:
1) Xabar matnida:  emoji("ROCKET")  ->  <tg-emoji emoji-id="...">🚀</tg-emoji>
2) Tugmada (raw):  ICON["ROCKET"]   ->  faqat ID (icon_custom_emoji_id uchun)

Premium emoji ko'rinmasa Telegram avtomatik fallback (oddiy emoji) ko'rsatadi.
"""

# ─── nom -> (custom_emoji_id, fallback_emoji) ───────────────────────
CATALOG: dict[str, tuple[str, str]] = {
    "WAVE":     ("5816508088227730739", "👋"),
    "ROCKET":   ("5895720492190404869", "🚀"),
    "STAR":     ("5895702479097564641", "⭐️"),
    "EDIT":     ("5897737086710059363", "📝"),
    "CLOCK":    ("5816934234882839927", "⏰"),
    "CHAT":     ("5985293048760766504", "💬"),
    "GROUP":    ("5933769822214034093", "💬"),
    "USER":     ("5897785405092138893", "👨‍💻"),
    "USERS":    ("5933769822214034093", "👥"),
    "GEAR":     ("5895592588064328942", "⚙️"),
    "INFO":     ("5816742056571180106", "ℹ️"),
    "OK":       ("5895231943955451762", "✅"),
    "WARN":     ("5852487725051023314", "⛔"),
    "CROWN":    ("5895709153476742796", "👑"),
    "PHONE":    ("6037232942969786590", "📱"),
    "QR":       ("6037193420680729470", "📲"),
    "KEY":      ("5897604269141398480", "🔐"),
    "BACK":     ("5985764515910784774", "⬅️"),
    "PLAY":     ("5895705279416241926", "▶️"),
    "STOP":     ("5852753450382659113", "🔴"),
    "SHOP":     ("5895288113537748673", "🏪"),
    "TOOLS":    ("5895483165182529286", "🛡"),
    "BOOK":     ("5895583431194054511", "🌟"),
    "STATS":    ("5852974147277164834", "⭐"),
    "CHECK":    ("5895222507912302025", "✔️"),
    "CROSS":    ("5852812849780362931", "❌"),
    "MONEY":    ("5895720492190404869", "💰"),
    "GIFT":     ("5938540495792771769", "🎁"),
    "CARD":     ("5895483809427624713", "💳"),
    "GREEN":    ("5938173980463599579", "🟢"),
    "RED":      ("5938476956046593663", "🔴"),
    "TIMER":    ("5897851045077324433", "⏱"),
    "REPLY":    ("5985293048760766504", "🔄"),
    "PIN":      ("5816598974030681170", "📍"),
    "TARGET":   ("5938138877695888929", "🎯"),
    "CALENDAR": ("5895731156594200261", "📅"),
    "MENTION":  ("5985293048760766504", "💬"),
    "INFINITY": ("5895511022340411227", "♾"),
    "CAMERA":   ("5895731156594200261", "📷"),
    "REFRESH":  ("5897851045077324433", "🔄"),
}

# Oddiy emoji (ReplyKeyboard tugmalari uchun — premium ishlamaydi u yerda)
PLAIN: dict[str, str] = {name: fb for name, (_id, fb) in CATALOG.items()}


def emoji(name: str) -> str:
    """Xabar matnida premium emoji HTML tegi (HTML parse_mode kerak)."""
    eid, fb = CATALOG.get(name, ("", "•"))
    if not eid:
        return fb
    return f'<tg-emoji emoji-id="{eid}">{fb}</tg-emoji>'


def oe(name: str) -> str:
    """Oddiy emoji (ReplyKeyboard uchun)."""
    return PLAIN.get(name, "•")


# Tugmalarda ishlatish uchun faqat ID lar (raw API icon_custom_emoji_id)
ICON: dict[str, str] = {name: eid for name, (eid, _fb) in CATALOG.items()}


# ═══ Eski kod bilan moslik (avvalgi handlerlar uchun) ═══════════════
def pe(name: str) -> str:
    return emoji(name)

E_WAVE="WAVE"; E_STAR="STAR"; E_ROCKET="ROCKET"; E_EDIT="EDIT"
E_CLOCK="CLOCK"; E_CHAT="CHAT"; E_GROUP="GROUP"; E_USER="USER"
E_GEAR="GEAR"; E_INFO="INFO"; E_OK="OK"; E_WARN="WARN"
E_PHONE="PHONE"; E_QR="QR"; E_KEY="KEY"; E_BACK="BACK"
E_ID="INFO"; E_MONEY="MONEY"

def tg_emoji(name, fallback=""):
    if name in CATALOG: return emoji(name)
    if str(name).isdigit(): return f'<tg-emoji emoji-id="{name}">{fallback}</tg-emoji>'
    return fallback or name

def eW(): return emoji("WAVE")
def eST(): return emoji("STAR")
def eMN(): return emoji("MONEY")
def eUS(): return emoji("USER")
def eIN(): return emoji("INFO")
def eID(): return emoji("INFO")
def eWL(): return emoji("STAR")
def eOK(): return emoji("OK")
def eCL(): return emoji("CLOCK")
def eWN(): return emoji("WARN")
def eRK(): return emoji("ROCKET")
def eGR(): return emoji("GROUP")
def eGE(): return emoji("GEAR")
def eQR(): return emoji("QR")
def ePH(): return emoji("PHONE")
