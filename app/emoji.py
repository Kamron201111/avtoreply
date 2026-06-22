"""
Premium emoji va rangli inline tugma yordamchilari.

Bot API 9.4 (2026-02-09) xususiyatlari:
  • style  — tugma rangi: "primary" (ko'k), "success" (yashil), "danger" (qizil)
  • icon_custom_emoji_id — tugmadagi premium emoji ID

MUHIM:
  • style faqat 2026-02-09 dan keyingi Telegram klientlarida ko'rinadi.
  • icon_custom_emoji_id faqat Fragment'da username sotib olgan bot,
    YOKI bot egasida Telegram Premium bo'lsa ishlaydi.
  • Xabar matnida premium emoji uchun: <tg-emoji emoji-id="...">😀</tg-emoji>
    (parse_mode="HTML" bilan)
"""

# ─── Premium Emoji ID lar (Elder Stars'dan olingan namuna) ──────────
E_WAVE = "5472427507842032538"      # 👋
E_STAR = "5807791714093502248"      # ⭐️
E_MONEY = "5258204546391351475"     # 💰
E_USER = "6035084557378654059"      # 👤
E_INFO = "5974193375799152241"      # ℹ️
E_ID = "5811989245761426317"        # 🆔
E_WALLET = "5472363448404809929"    # 👛
E_OK = "5774022692642492953"        # ✅
E_CARD = "5927169041595634481"      # 💳
E_CLOCK = "5778420863707649338"     # ⏰
E_WARN = "5316554554735607106"      # ⚠️
E_EDIT = "5766915217552315762"      # ✏️
E_BACK = "6039539366177541657"      # ⬅️
E_CHAT = "6030776052345737530"      # 💬
E_ROCKET = "5345913151579787927"    # 🚀
E_GROUP = "5341715473882955310"     # 💬 guruh
E_PLAY = "5237699328843200968"      # ▶️
E_STOP = "5240241223632954241"      # ⏹
E_GEAR = "5235837920081887219"      # ⚙️
E_QR = "5253742917460009731"        # 📲
E_PHONE = "5253850106008670281"     # 📱
E_KEY = "5253603586894200061"       # 🔑


def tg_emoji(emoji_id: str, fallback: str) -> str:
    """Xabar MATNIDA premium emoji (HTML parse_mode kerak)."""
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'


# Tayyor matn-emoji yordamchilari
def eW() -> str: return tg_emoji(E_WAVE, "👋")
def eST() -> str: return tg_emoji(E_STAR, "⭐️")
def eMN() -> str: return tg_emoji(E_MONEY, "💰")
def eUS() -> str: return tg_emoji(E_USER, "👤")
def eIN() -> str: return tg_emoji(E_INFO, "ℹ️")
def eID() -> str: return tg_emoji(E_ID, "🆔")
def eWL() -> str: return tg_emoji(E_WALLET, "👛")
def eOK() -> str: return tg_emoji(E_OK, "✅")
def eCL() -> str: return tg_emoji(E_CLOCK, "⏰")
def eWN() -> str: return tg_emoji(E_WARN, "⚠️")
def eRK() -> str: return tg_emoji(E_ROCKET, "🚀")
def eGR() -> str: return tg_emoji(E_GROUP, "💬")
def eGE() -> str: return tg_emoji(E_GEAR, "⚙️")
def eQR() -> str: return tg_emoji(E_QR, "📲")
def ePH() -> str: return tg_emoji(E_PHONE, "📱")
