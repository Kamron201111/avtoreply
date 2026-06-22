# 🚀 AUTO HABAR PRO — Telegram Avto-Xabar Boti

Foydalanuvchi akkauntini **QR kod** yoki **SMS** orqali ulab, tanlangan guruhlarga belgilangan interval bilan avtomatik xabar yuboradigan bot.

**Texnologiyalar:** aiogram 3.x · Telethon (userbot) · PostgreSQL · Bot API 9.4 (rangli tugmalar + premium emoji)

---

## ✨ Imkoniyatlar

| Funksiya | Tavsif |
|----------|--------|
| 📲 **QR ulash** | QR kodni skaner qilib akkaunt ulash |
| 📱 **SMS ulash** | Telefon raqami + kod orqali ulash (2FA qo'llab-quvvatlanadi) |
| 💬 **Avto-xabar** | Guruhlarga interval bilan avtomatik xabar |
| 🔄 **Autoreply** | DM'ga avtomatik javob (siz onlayn bo'lmaganda) |
| ⏰ **Interval** | 2 daqiqadan 3 soatgacha yoki qo'lda |
| 📊 **Statistika** | Yuborilgan/xato xabarlar hisobi |
| 👑 **Premium** | Tarif tizimi (admin beradi) |
| 🛠 **Admin panel** | Broadcast, foydalanuvchilar, premium boshqaruvi |

---

## 🎨 Premium Emoji va Rangli Tugmalar

Bu bot **Bot API 9.4** (2026-02-09) xususiyatlaridan foydalanadi:

```python
# app/keyboards/builder.py
btn("Ishga tushurish", "start", emoji="5807791714093502248", style="success")
#                                      ↑ premium emoji ID        ↑ yashil rang
```

- **`style`** — tugma rangi: `"primary"` (ko'k), `"success"` (yashil), `"danger"` (qizil)
- **`icon_custom_emoji_id`** — tugmadagi premium emoji

⚠️ **Muhim shartlar:**
- `style` faqat **2026-02-09 dan keyingi** Telegram klientlarida ko'rinadi (eski klientlar tugmani rangsiz ko'rsatadi).
- `icon_custom_emoji_id` faqat **Fragment'da username sotib olgan** bot, YOKI bot egasida **Telegram Premium** bo'lsa ishlaydi.
- Xabar **matnida** premium emoji: `<tg-emoji emoji-id="...">😀</tg-emoji>` (HTML parse_mode bilan).

---

## 📦 O'rnatish (lokal)

```bash
# 1. Repozitoriyani klonlang
git clone <repo> && cd autohabar_py

# 2. Kutubxonalar
pip install -r requirements.txt

# 3. .env faylini sozlang
cp .env.example .env
nano .env

# 4. PostgreSQL bazasini yarating
createdb autohabar

# 5. Ishga tushiring
python main.py
```

---

## 🔑 .env Sozlamalari

```ini
BOT_TOKEN=...          # @BotFather dan
TG_API_ID=...          # my.telegram.org/apps dan
TG_API_HASH=...        # my.telegram.org/apps dan
ADMIN_IDS=123456789    # Sizning Telegram ID
ADMIN_USERNAME=admin

DB_HOST=localhost
DB_PORT=5432
DB_NAME=autohabar
DB_USER=postgres
DB_PASS=...
```

**API ID/HASH olish:** [my.telegram.org/apps](https://my.telegram.org/apps) ga kiring → "API development tools" → yangi ilova yarating.

---

## ☁️ Railway Deploy

1. **GitHub'ga push qiling** (`.env` va `sessions/` siz)
2. [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
3. **New** → **Database** → **PostgreSQL** qo'shing
4. **Variables** bo'limiga `.env` qiymatlarini kiriting:
   - PostgreSQL o'zgaruvchilari Railway tomonidan avtomatik beriladi (`PGHOST`, `PGPORT` va h.k.)
   - Ularni `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASS` ga moslang
5. Deploy avtomatik boshlanadi — `python main.py` ishga tushadi

> **Eslatma:** Bot **polling** rejimida ishlaydi (webhook emas), shuning uchun Railway'da alohida domen sozlash shart emas. `worker` turidagi service sifatida ishlaydi.

---

## 📁 Loyiha tuzilmasi

```
autohabar_py/
├── main.py                      # Ishga tushirish yorlig'i
├── requirements.txt
├── .env.example
├── Procfile / railway.json      # Railway config
│
└── app/
    ├── main.py                  # Asosiy bot logikasi
    ├── config.py                # .env sozlamalari
    ├── emoji.py                 # Premium emoji ID lar
    ├── states.py                # FSM holatlar
    │
    ├── database/
    │   └── db.py                # PostgreSQL (asyncpg)
    │
    ├── keyboards/
    │   ├── builder.py           # btn() — rangli+emoji tugma
    │   └── menus.py             # Barcha klaviaturalar
    │
    ├── userbot/
    │   ├── login.py             # QR + SMS + 2FA ulash
    │   └── manager.py           # Guruhga yuborish, autoreply
    │
    ├── handlers/
    │   ├── start.py             # /start, asosiy menyu
    │   ├── accounts.py          # Akkaunt ulash
    │   ├── manage.py            # Guruh/xabar/interval/autoreply
    │   └── admin.py             # Admin panel
    │
    └── services/
        └── scheduler.py         # Avto-yuborish fon vazifasi
```

---

## 🔄 Qanday ishlaydi?

1. Foydalanuvchi **/start** → asosiy menyu
2. **Akkaunt qo'shish** → QR yoki SMS → Telethon `session_string` saqlanadi
3. Akkaunt guruhlari avtomatik yuklanadi
4. Foydalanuvchi **xabar matni** + **interval** + **guruhlar** ni sozlaydi
5. **Ishga tushuradi** → `scheduler.py` har 30 soniyada tekshiradi
6. Vaqt yetganda → akkaunt nomidan guruhlarga xabar yuboriladi
7. Statistika DB ga yoziladi, keyingi yuborish vaqti belgilanadi

---

## ⚠️ Muhim eslatmalar

- **Userbot riski:** Telegram qoidalariga ko'ra avtomatlashtirilgan spam akkauntni cheklashga olib kelishi mumkin. Faol intervallarni mantiqiy belgilang (juda tez emas).
- **Flood himoyasi:** Bot guruhlar orasida 2 soniya pauza qiladi va `FloodWaitError` ni qayta ishlaydi.
- **Sessiya xavfsizligi:** `session_string` bazada saqlanadi — bazani himoyalang.
- Bot **rasm/fayl** emas, **matn** xabar yuboradi (userbot file_id cheklovi). Kerak bo'lsa kengaytirish mumkin.

---

## 📞 Qo'llab-quvvatlash

Savol bo'lsa admin bilan bog'laning (`.env` dagi `ADMIN_USERNAME`).
