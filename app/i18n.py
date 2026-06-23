"""
3 tilli matnlar (uz / ru / en) + premium emoji.

T(key, lang, **kwargs) — tarjima qaytaradi.
Emoji {e_NAME} formatida matn ichida, T() avtomatik almashtiradi.
"""
from app.emoji import emoji as _em

LANGS = {"uz": "🇺🇿 O'zbekcha", "ru": "🇷🇺 Русский", "en": "🇬🇧 English"}

# ─── Barcha matnlar ─────────────────────────────────────────────────
TEXTS: dict[str, dict[str, str]] = {

    # ═══ TIL TANLASH ═══
    "choose_lang": {
        "uz": "🌐 Tilni tanlang\nВыберите язык\nChoose language",
        "ru": "🌐 Tilni tanlang\nВыберите язык\nChoose language",
        "en": "🌐 Tilni tanlang\nВыберите язык\nChoose language",
    },
    "lang_set": {
        "uz": "{e_OK} Til o'rnatildi: <b>O'zbekcha</b>",
        "ru": "{e_OK} Язык установлен: <b>Русский</b>",
        "en": "{e_OK} Language set: <b>English</b>",
    },

    # ═══ WELCOME ═══
    "welcome": {
        "uz": ("{e_ROCKET} <b>AUTO HABAR PRO</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
               "Salom, <b>{name}</b> {e_WAVE}\n\n"
               "<blockquote>› Profil (akkaunt) qo'shing\n› Guruhlarni sozlang\n"
               "› Habar matnini yozing\n› Autohabarni ishga tushuring</blockquote>"),
        "ru": ("{e_ROCKET} <b>AUTO HABAR PRO</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
               "Привет, <b>{name}</b> {e_WAVE}\n\n"
               "<blockquote>› Добавьте профиль (аккаунт)\n› Настройте группы\n"
               "› Напишите текст\n› Запустите авторассылку</blockquote>"),
        "en": ("{e_ROCKET} <b>AUTO HABAR PRO</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
               "Hello, <b>{name}</b> {e_WAVE}\n\n"
               "<blockquote>› Add a profile (account)\n› Set up groups\n"
               "› Write your message\n› Start auto-posting</blockquote>"),
    },

    # ═══ ASOSIY MENYU TUGMALARI (reply) ═══
    "btn_autosend": {"uz": "🚀 Autohabar yuborish", "ru": "🚀 Авторассылка", "en": "🚀 Auto-post"},
    "btn_message":  {"uz": "📝 Habar matni", "ru": "📝 Текст", "en": "📝 Message"},
    "btn_interval": {"uz": "⏰ Interval", "ru": "⏰ Интервал", "en": "⏰ Interval"},
    "btn_groups":   {"uz": "💬 Guruhlarni sozlash", "ru": "💬 Группы", "en": "💬 Groups"},
    "btn_profiles": {"uz": "👥 Profillar", "ru": "👥 Профили", "en": "👥 Profiles"},
    "btn_pro":      {"uz": "👑 Pro tarif", "ru": "👑 Pro тариф", "en": "👑 Pro plan"},
    "btn_cabinet":  {"uz": "👤 Kabinet", "ru": "👤 Кабинет", "en": "👤 Cabinet"},
    "btn_settings": {"uz": "⚙️ Sozlamalar", "ru": "⚙️ Настройки", "en": "⚙️ Settings"},
    "btn_calendar": {"uz": "📅 Kalendar", "ru": "📅 Календарь", "en": "📅 Calendar"},
    "btn_tools":    {"uz": "🔧 Foydali funksiyalar", "ru": "🔧 Полезное", "en": "🔧 Tools"},
    "btn_stats":    {"uz": "📊 Statistika", "ru": "📊 Статистика", "en": "📊 Stats"},
    "btn_help":     {"uz": "🎧 Yordam", "ru": "🎧 Помощь", "en": "🎧 Help"},
    "btn_guide":    {"uz": "📕 Qo'llanma", "ru": "📕 Руководство", "en": "📕 Guide"},
    "btn_autoreply":{"uz": "🔄 Autoreply", "ru": "🔄 Автоответ", "en": "🔄 Autoreply"},
    "btn_admin":    {"uz": "🛠 Admin panel", "ru": "🛠 Админ панель", "en": "🛠 Admin panel"},

    # ═══ UMUMIY ═══
    "back":   {"uz": "⬅️ Orqaga", "ru": "⬅️ Назад", "en": "⬅️ Back"},
    "close":  {"uz": "✖️ Yopish", "ru": "✖️ Закрыть", "en": "✖️ Close"},
    "home":   {"uz": "🏠 Bosh sahifa", "ru": "🏠 Главная", "en": "🏠 Home"},
    "cancel": {"uz": "Bekor qilish", "ru": "Отмена", "en": "Cancel"},
    "no_account": {
        "uz": "{e_WARN} <b>Avval profil (akkaunt) qo'shing!</b>\n\n«👥 Profillar» bo'limiga o'ting.",
        "ru": "{e_WARN} <b>Сначала добавьте профиль!</b>\n\nПерейдите в «👥 Профили».",
        "en": "{e_WARN} <b>Add a profile first!</b>\n\nGo to «👥 Profiles».",
    },

    # ═══ BOSHQARUV PANEL (Autohabar) ═══
    "panel_title":  {"uz": "Boshqaruv panel", "ru": "Панель управления", "en": "Control panel"},
    "p_profile":    {"uz": "Profil", "ru": "Профиль", "en": "Profile"},
    "p_status":     {"uz": "Holat", "ru": "Статус", "en": "Status"},
    "p_msgtype":    {"uz": "Xabar turi", "ru": "Тип сообщения", "en": "Message type"},
    "p_groups":     {"uz": "Guruhlar", "ru": "Группы", "en": "Groups"},
    "p_interval":   {"uz": "Interval", "ru": "Интервал", "en": "Interval"},
    "p_autodel":    {"uz": "Avto-o'chish", "ru": "Автоудаление", "en": "Auto-delete"},
    "p_mention":    {"uz": "Mention", "ru": "Упоминание", "en": "Mention"},
    "st_running":   {"uz": "🟢 Ishlamoqda", "ru": "🟢 Работает", "en": "🟢 Running"},
    "st_stopped":   {"uz": "{e_RED} O'chiq", "ru": "{e_RED} Выключено", "en": "{e_RED} Off"},
    "infinite":     {"uz": "♾ Cheksiz", "ru": "♾ Без лимита", "en": "♾ Unlimited"},
    "on":           {"uz": "Yoqilgan", "ru": "Включено", "en": "On"},
    "off":          {"uz": "O'chiq", "ru": "Выключено", "en": "Off"},
    "mtype_text":   {"uz": "Matn", "ru": "Текст", "en": "Text"},
    "mtype_photo":  {"uz": "Rasm+matn", "ru": "Фото+текст", "en": "Photo+text"},
    "mtype_button": {"uz": "Tugmali", "ru": "С кнопкой", "en": "With button"},

    "btn_start":    {"uz": "Ishga tushurish", "ru": "Запустить", "en": "Start"},
    "btn_stop":     {"uz": "To'xtatish", "ru": "Остановить", "en": "Stop"},
    "btn_p_stats":  {"uz": "Statistika", "ru": "Статистика", "en": "Stats"},
    "btn_autodel":  {"uz": "Avto-o'chirish taymeri", "ru": "Таймер автоудаления", "en": "Auto-delete timer"},

    "need_msg":     {"uz": "{e_WARN} Avval «Habar matni» ni sozlang!", "ru": "{e_WARN} Сначала настройте текст!", "en": "{e_WARN} Set the message first!"},
    "need_groups":  {"uz": "{e_WARN} Avval guruh tanlang!", "ru": "{e_WARN} Сначала выберите группы!", "en": "{e_WARN} Select groups first!"},
    "started":      {"uz": "🟢 Ishga tushdi!", "ru": "🟢 Запущено!", "en": "🟢 Started!"},
    "stopped":      {"uz": "🔴 To'xtatildi", "ru": "🔴 Остановлено", "en": "🔴 Stopped"},

    # ═══ MENTION ogohlantirish ═══
    "mention_warn": {
        "uz": ("{e_WARN} <b>Mention — nima qiladi?</b>\n\n"
               "Har xabar yuborilganda guruh a'zolaridan birini @mention qiladi.\n\n"
               "• Spam xavfi oshadi — Telegram akkauntni cheklashi mumkin\n"
               "• Guruhdan chiqarib yuborilish ehtimoli bor\n"
               "• Ko'p guruhli akkauntlarda PEER_FLOOD xavfi yuqori\n\n"
               "Haqiqatan ham yoqmoqchimisiz?"),
        "ru": ("{e_WARN} <b>Упоминание — что это?</b>\n\n"
               "При каждой отправке упоминает @одного из участников группы.\n\n"
               "• Риск спама — Telegram может ограничить аккаунт\n"
               "• Возможен бан из группы\n"
               "• Высокий риск PEER_FLOOD\n\n"
               "Точно включить?"),
        "en": ("{e_WARN} <b>Mention — what is it?</b>\n\n"
               "Mentions @one group member on each send.\n\n"
               "• Higher spam risk — Telegram may limit the account\n"
               "• Possible ban from the group\n"
               "• High PEER_FLOOD risk\n\n"
               "Are you sure?"),
    },
    "yes_understand": {"uz": "Ha, tushundim {e_OK}", "ru": "Да, понятно {e_OK}", "en": "Yes, I understand {e_OK}"},

    # ═══ HABAR MATNI ═══
    "msg_title": {"uz": "Habarni sozlash", "ru": "Настройка сообщения", "en": "Message setup"},
    "msg_curtype": {"uz": "Joriy tur", "ru": "Текущий тип", "en": "Current type"},
    "msg_msg": {"uz": "Xabar", "ru": "Сообщение", "en": "Message"},
    "msg_set": {"uz": "{e_OK} Sozlangan", "ru": "{e_OK} Настроено", "en": "{e_OK} Set"},
    "msg_notset": {"uz": "{e_RED} Sozlanmagan", "ru": "{e_RED} Не настроено", "en": "{e_RED} Not set"},
    "fwd_pro": {"uz": "Forward faqat Pro tarifda {e_CARD}", "ru": "Forward только в Pro {e_CARD}", "en": "Forward only in Pro {e_CARD}"},
    "choose_msgtype": {"uz": "👇 Xabar turini tanlang:", "ru": "👇 Выберите тип:", "en": "👇 Choose type:"},
    "b_text": {"uz": "📝 Matn", "ru": "📝 Текст", "en": "📝 Text"},
    "b_photo": {"uz": "🖼 Rasm+matn", "ru": "🖼 Фото+текст", "en": "🖼 Photo+text"},
    "b_fwd": {"uz": "↪️ Forward 🔒", "ru": "↪️ Forward 🔒", "en": "↪️ Forward 🔒"},
    "b_btnmsg": {"uz": "⚙️ Tugmali habar", "ru": "⚙️ С кнопкой", "en": "⚙️ With button"},
    "b_multi": {"uz": "🗂 Turli habarlar 🔒", "ru": "🗂 Разные 🔒", "en": "🗂 Multiple 🔒"},
    "send_text": {"uz": "{e_EDIT} Guruhlarga yuboriladigan matnni yuboring:", "ru": "{e_EDIT} Отправьте текст:", "en": "{e_EDIT} Send the text:"},
    "send_photo": {"uz": "🖼 Rasmni izoh bilan yuboring:", "ru": "🖼 Отправьте фото с подписью:", "en": "🖼 Send a photo with caption:"},
    "msg_saved": {"uz": "{e_OK} Xabar saqlandi!", "ru": "{e_OK} Сообщение сохранено!", "en": "{e_OK} Message saved!"},
    "pro_only": {"uz": "🔒 Bu funksiya faqat Pro tarifda!", "ru": "🔒 Только в Pro тарифе!", "en": "🔒 Pro plan only!"},
    "soon": {"uz": "Tez orada qo'shiladi.", "ru": "Скоро будет.", "en": "Coming soon."},

    # ═══ INTERVAL ═══
    "int_title": {"uz": "Habar oralig'i", "ru": "Интервал отправки", "en": "Send interval"},
    "int_cur": {"uz": "Joriy interval", "ru": "Текущий интервал", "en": "Current interval"},
    "int_choose": {"uz": "Kerakli vaqtni tanlang:", "ru": "Выберите время:", "en": "Choose time:"},
    "int_manual": {"uz": "📝 Qo'lda kiritish", "ru": "📝 Ввести вручную", "en": "📝 Manual"},
    "int_what_btn": {"uz": "⁉️ Interval nima", "ru": "⁉️ Что это", "en": "⁉️ What is it"},
    "int_what": {
        "uz": "Interval — har bir guruhga xabar yuborish orasidagi vaqt. Masalan 5 daqiqa = har 5 daqiqada barcha guruhlarga yuboriladi.",
        "ru": "Интервал — время между отправками в группы. Например 5 минут = каждые 5 минут во все группы.",
        "en": "Interval — time between sends to groups. E.g. 5 min = every 5 minutes to all groups.",
    },
    "int_manual_q": {"uz": "{e_EDIT} Daqiqalarda son kiriting (masalan 25):", "ru": "{e_EDIT} Введите минуты (например 25):", "en": "{e_EDIT} Enter minutes (e.g. 25):"},
    "int_set": {"uz": "✅ Interval {n} daqiqa o'rnatildi!", "ru": "✅ Интервал {n} мин!", "en": "✅ Interval set to {n} min!"},
    "int_free_limit": {"uz": "⚠️ Bepul tarifda minimal {n} daqiqa. Pro oling!", "ru": "⚠️ В бесплатном минимум {n} мин. Купите Pro!", "en": "⚠️ Free min {n} min. Get Pro!"},
    "only_number": {"uz": "{e_WARN} Faqat son kiriting.", "ru": "{e_WARN} Только число.", "en": "{e_WARN} Numbers only."},

    # ═══ GURUHLAR ═══
    "grp_title": {"uz": "{e_TARGET} Guruhlarni sozlash", "ru": "{e_TARGET} Настройка групп", "en": "{e_TARGET} Group setup"},
    "grp_q": {"uz": "Qaysi guruhlarga xabar yuboramiz?", "ru": "В какие группы отправлять?", "en": "Which groups to send to?"},
    "grp_selected": {"uz": "Tanlangan", "ru": "Выбрано", "en": "Selected"},
    "grp_notselected": {"uz": "Tanlanmagan", "ru": "Не выбрано", "en": "Not selected"},
    "grp_cur": {"uz": "Hozirgi tanlov", "ru": "Текущий выбор", "en": "Current choice"},
    "grp_all_lbl": {"uz": "Hamma guruhlarga", "ru": "Все группы", "en": "All groups"},
    "grp_pick_lbl": {"uz": "O'zim tanlayman", "ru": "Выбрать самому", "en": "Pick myself"},
    "grp_choose": {"uz": "🗒 Guruhlarni tanlang", "ru": "🗒 Выберите группы", "en": "🗒 Choose groups"},
    "b_grp_all": {"uz": "➕ Hamma guruhlarga", "ru": "➕ Все группы", "en": "➕ All groups"},
    "b_grp_pick": {"uz": "✔️ O'zim tanlayman", "ru": "✔️ Выбрать самому", "en": "✔️ Pick myself"},
    "b_grp_lists": {"uz": "📋 Ro'yxatlar", "ru": "📋 Списки", "en": "📋 Lists"},
    "b_grp_add": {"uz": "➕ Qo'shish", "ru": "➕ Добавить", "en": "➕ Add"},
    "b_grp_del": {"uz": "🗑 O'chirish", "ru": "🗑 Удалить", "en": "🗑 Delete"},
    "grp_count": {"uz": "{n} ta tanlangan", "ru": "выбрано {n}", "en": "{n} selected"},
    "grp_loading": {"uz": "🔄 Guruhlar yuklanmoqda...", "ru": "🔄 Загрузка групп...", "en": "🔄 Loading groups..."},
    "grp_loaded": {"uz": "✅ {n} ta guruh", "ru": "✅ {n} групп", "en": "✅ {n} groups"},
    "grp_empty": {"uz": "Guruh yo'q. «Qo'shish» bosing.", "ru": "Нет групп. Нажмите «Добавить».", "en": "No groups. Tap «Add»."},
    "grp_all_on": {"uz": "✅ Hamma guruh tanlandi", "ru": "✅ Все группы выбраны", "en": "✅ All selected"},
    "grp_cleared": {"uz": "🗑 Hammasi o'chirildi", "ru": "🗑 Все удалены", "en": "🗑 All cleared"},

    # ═══ PROFILLAR ═══
    "prof_title": {"uz": "{e_USERS} Profillar", "ru": "{e_USERS} Профили", "en": "{e_USERS} Profiles"},
    "prof_count": {"uz": "Ulangan akkauntlar: <b>{n}</b> ta", "ru": "Подключено: <b>{n}</b>", "en": "Connected: <b>{n}</b>"},
    "prof_none": {"uz": "Hali akkaunt ulanmagan.", "ru": "Нет аккаунтов.", "en": "No accounts yet."},
    "prof_manage": {"uz": "Boshqarish uchun tanlang:", "ru": "Выберите для управления:", "en": "Select to manage:"},
    "b_add_acc": {"uz": "➕ Akkaunt qo'shish", "ru": "➕ Добавить аккаунт", "en": "➕ Add account"},
    "b_del_acc": {"uz": "🗑 Profilni uzish", "ru": "🗑 Отключить профиль", "en": "🗑 Disconnect"},
    "acc_deleted": {"uz": "🗑 Profil o'chirildi", "ru": "🗑 Профиль удалён", "en": "🗑 Profile removed"},

    # ═══ AKKAUNT ULASH ═══
    "link_title": {"uz": "{e_QR} Akkaunt ulash", "ru": "{e_QR} Подключение", "en": "{e_QR} Link account"},
    "link_choose": {"uz": "Ulash usulini tanlang:", "ru": "Выберите способ:", "en": "Choose method:"},
    "link_qr_info": {"uz": "📲 <b>QR kod</b> — tez, telefon orqali skaner", "ru": "📲 <b>QR-код</b> — быстро, сканом", "en": "📲 <b>QR code</b> — fast, by scan"},
    "link_sms_info": {"uz": "📱 <b>SMS</b> — telefon raqamiga kod", "ru": "📱 <b>SMS</b> — код на номер", "en": "📱 <b>SMS</b> — code to phone"},
    "b_link_qr": {"uz": "📲 QR kod orqali", "ru": "📲 Через QR-код", "en": "📲 Via QR code"},
    "b_link_sms": {"uz": "📱 SMS orqali", "ru": "📱 Через SMS", "en": "📱 Via SMS"},
    "qr_making": {"uz": "QR kod yaratilmoqda...", "ru": "Создаётся QR...", "en": "Generating QR..."},
    "qr_caption": {
        "uz": ("{e_QR} <b>QR kod orqali ulash</b>\n\n"
               "1️⃣ Telefonда Telegram'ni oching\n2️⃣ Sozlamalar → Qurilmalar\n"
               "3️⃣ Kompyuterни ulash\n4️⃣ Ushbu QR'ni skaner qiling\n\n"
               "{e_CLOCK} QR 60 soniya amal qiladi."),
        "ru": ("{e_QR} <b>Вход по QR-коду</b>\n\n"
               "1️⃣ Откройте Telegram на телефоне\n2️⃣ Настройки → Устройства\n"
               "3️⃣ Подключить устройство\n4️⃣ Сканируйте QR\n\n"
               "{e_CLOCK} QR действует 60 секунд."),
        "en": ("{e_QR} <b>Login via QR</b>\n\n"
               "1️⃣ Open Telegram on phone\n2️⃣ Settings → Devices\n"
               "3️⃣ Link Desktop Device\n4️⃣ Scan this QR\n\n"
               "{e_CLOCK} QR valid for 60 seconds."),
    },
    "qr_refresh": {"uz": "🔄 Yangilash", "ru": "🔄 Обновить", "en": "🔄 Refresh"},
    "qr_expired": {"uz": "{e_CLOCK} QR muddati tugadi. «Yangilash» bosing.", "ru": "{e_CLOCK} QR истёк. Нажмите «Обновить».", "en": "{e_CLOCK} QR expired. Tap «Refresh»."},
    "sms_phone": {
        "uz": "{e_PHONE} <b>SMS orqali ulash</b>\n\nTelefon raqamingizni yuboring:\n<code>+998901234567</code>",
        "ru": "{e_PHONE} <b>Вход по SMS</b>\n\nОтправьте номер:\n<code>+998901234567</code>",
        "en": "{e_PHONE} <b>Login via SMS</b>\n\nSend your phone:\n<code>+998901234567</code>",
    },
    "phone_bad": {"uz": "{e_WARN} Raqam noto'g'ri. Format: <code>+998901234567</code>", "ru": "{e_WARN} Неверный номер.", "en": "{e_WARN} Bad number."},
    "code_sending": {"uz": "{e_CLOCK} Kod yuborilmoqda...", "ru": "{e_CLOCK} Отправка кода...", "en": "{e_CLOCK} Sending code..."},
    "code_sent": {
        "uz": ("{e_OK} Kod yuborildi!\n\n📨 <b>{phone}</b> ga kelgan kodni kiriting.\n\n"
               "⚠️ <i>Kodni bo'shliq bilan yozing: «1 2 3 4 5» — Telegram o'chirib yubormasligi uchun.</i>"),
        "ru": ("{e_OK} Код отправлен!\n\n📨 Введите код с <b>{phone}</b>.\n\n"
               "⚠️ <i>Пишите код с пробелами: «1 2 3 4 5».</i>"),
        "en": ("{e_OK} Code sent!\n\n📨 Enter the code sent to <b>{phone}</b>.\n\n"
               "⚠️ <i>Type code with spaces: «1 2 3 4 5».</i>"),
    },
    "checking": {"uz": "{e_CLOCK} Tekshirilmoqda...", "ru": "{e_CLOCK} Проверка...", "en": "{e_CLOCK} Checking..."},
    "code_bad": {"uz": "{e_WARN} Kod faqat raqam.", "ru": "{e_WARN} Только цифры.", "en": "{e_WARN} Digits only."},
    "need_2fa": {"uz": "🔐 <b>2FA parol kerak.</b>\n\nParolingizni yuboring:", "ru": "🔐 <b>Нужен пароль 2FA.</b>\n\nОтправьте пароль:", "en": "🔐 <b>2FA password needed.</b>\n\nSend password:"},
    "pwd_check": {"uz": "{e_CLOCK} Parol tekshirilmoqda...", "ru": "{e_CLOCK} Проверка пароля...", "en": "{e_CLOCK} Checking password..."},
    "already_linked": {
        "uz": "{e_WARN} Bu akkaunt allaqachon boshqa foydalanuvchi tomonidan ulangan! Bitta akkaunt faqat bir marta ulanadi.",
        "ru": "{e_WARN} Этот аккаунт уже подключён другим пользователем! Один аккаунт — одно подключение.",
        "en": "{e_WARN} This account is already linked by another user! One account, one link.",
    },
    "link_ok": {
        "uz": "{e_OK} <b>Akkaunt ulandi!</b>\n\n{e_USER} <b>{uname}</b>\n📱 <code>{phone}</code>\n{e_CLOCK} Guruhlar yuklanmoqda...",
        "ru": "{e_OK} <b>Аккаунт подключён!</b>\n\n{e_USER} <b>{uname}</b>\n📱 <code>{phone}</code>\n{e_CLOCK} Загрузка групп...",
        "en": "{e_OK} <b>Account linked!</b>\n\n{e_USER} <b>{uname}</b>\n📱 <code>{phone}</code>\n{e_CLOCK} Loading groups...",
    },
    "link_done": {
        "uz": "{e_OK} <b>Akkaunt ulandi va sozlandi!</b>\n\n{e_USER} <b>{uname}</b>\n{e_GROUP} Guruhlar: <b>{n}</b> ta",
        "ru": "{e_OK} <b>Аккаунт готов!</b>\n\n{e_USER} <b>{uname}</b>\n{e_GROUP} Групп: <b>{n}</b>",
        "en": "{e_OK} <b>Account ready!</b>\n\n{e_USER} <b>{uname}</b>\n{e_GROUP} Groups: <b>{n}</b>",
    },
    "b_setup_acc": {"uz": "⚙️ Bu profilni sozlash", "ru": "⚙️ Настроить профиль", "en": "⚙️ Set up profile"},

    # ═══ KABINET ═══
    "cab_title": {"uz": "{e_USER} Sizning Kabinetingiz", "ru": "{e_USER} Ваш кабинет", "en": "{e_USER} Your Cabinet"},
    "cab_name": {"uz": "Ism", "ru": "Имя", "en": "Name"},
    "cab_phone": {"uz": "Raqam", "ru": "Номер", "en": "Phone"},
    "cab_stats": {"uz": "Statistika", "ru": "Статистика", "en": "Stats"},
    "cab_today": {"uz": "Bugun yuborildi", "ru": "Сегодня", "en": "Today"},
    "cab_total": {"uz": "Jami yuborilgan", "ru": "Всего", "en": "Total"},
    "cab_profiles": {"uz": "Jami profillar", "ru": "Профилей", "en": "Profiles"},
    "cab_tarif": {"uz": "Tarif", "ru": "Тариф", "en": "Plan"},
    "cab_free": {"uz": "Free", "ru": "Free", "en": "Free"},
    "cab_pro_no": {"uz": "Pro yo'q", "ru": "Нет Pro", "en": "No Pro"},
    "cab_pro_yes": {"uz": "Pro ✅", "ru": "Pro ✅", "en": "Pro ✅"},

    # ═══ SOZLAMALAR ═══
    "set_title": {"uz": "{e_GEAR} Umumiy sozlamalar", "ru": "{e_GEAR} Настройки", "en": "{e_GEAR} Settings"},
    "set_q": {"uz": "Qaysi sozlamani o'zgartirmoqchisiz?", "ru": "Что изменить?", "en": "What to change?"},
    "set_note": {"uz": "<i>Bu sozlamalar botning umumiy ishlashiga ta'sir qiladi.</i>", "ru": "<i>Влияет на общую работу бота.</i>", "en": "<i>Affects overall bot behavior.</i>"},
    "s_interval": {"uz": "⏰ Har bir habar oraligi", "ru": "⏰ Интервал отправки", "en": "⏰ Send interval"},
    "s_dm": {"uz": "💬 DM javob", "ru": "💬 Автоответ в ЛС", "en": "💬 DM reply"},
    "s_autosub": {"uz": "🔄 Avtomatik obuna", "ru": "🔄 Автоподписка", "en": "🔄 Auto-subscribe"},

    # ═══ DM JAVOB ═══
    "dm_title": {"uz": "💬 DM Javob", "ru": "💬 Автоответ в ЛС", "en": "💬 DM Reply"},
    "dm_menu_title": {"uz": "💬 DM Javob menyusi", "ru": "💬 Меню автоответа", "en": "💬 DM Reply menu"},
    "dm_desc": {
        "uz": ("Bot siz offline bo'lganda shaxsiy xabarlarga avtomatik javob beradi.\n\n"
               "🔄 Holat: {status}\n📝 Xabar: {msg}\n\n"
               "• Siz botga 5 daqiqa kirmasangiz — offline hisoblanasiz\n"
               "• Har bir chatga 10 soniyada 1 marta javob beriladi\n"
               "• Botlar va o'z xabarlaringizga javob berilmaydi"),
        "ru": ("Бот автоматически отвечает в ЛС, когда вы offline.\n\n"
               "🔄 Статус: {status}\n📝 Текст: {msg}\n\n"
               "• Offline через 5 минут бездействия\n"
               "• 1 ответ в 10 сек на чат\n"
               "• Боты и свои сообщения игнорируются"),
        "en": ("Bot auto-replies to DMs when you're offline.\n\n"
               "🔄 Status: {status}\n📝 Text: {msg}\n\n"
               "• Offline after 5 min inactivity\n"
               "• 1 reply per 10 sec per chat\n"
               "• Bots and own messages ignored"),
    },
    "dm_b_toggle_on": {"uz": "▶️ Ishga tushurish", "ru": "▶️ Запустить", "en": "▶️ Start"},
    "dm_b_run": {"uz": "▶️ Ishga tushurish/To'xtatish", "ru": "▶️ Запуск/Стоп", "en": "▶️ Start/Stop"},
    "dm_b_setmsg": {"uz": "✏️ Habar sozlash", "ru": "✏️ Настроить текст", "en": "✏️ Set message"},
    "dm_send_text": {"uz": "✏️ <b>DM javob matni</b>\n\nOffline bo'lganда yuboriladigan matnni kiriting:", "ru": "✏️ <b>Текст автоответа</b>\n\nВведите текст:", "en": "✏️ <b>DM reply text</b>\n\nEnter text:"},

    # ═══ AUTOREPLY (guruh reply) ═══
    "ar_title": {"uz": "💬 Autoreply", "ru": "💬 Автоответ", "en": "💬 Autoreply"},
    "ar_desc": {
        "uz": ("Tanlangan guruhlardagi oxirgi xabarga avtomatik reply qiladi.\n\n"
               "🔄 Holat: {status}\n📝 Xabar: {msg}\n{e_GROUP} Guruhlar: {n}"),
        "ru": ("Автоответ на последнее сообщение в выбранных группах.\n\n"
               "🔄 Статус: {status}\n📝 Текст: {msg}\n{e_GROUP} Группы: {n}"),
        "en": ("Auto-replies to the last message in selected groups.\n\n"
               "🔄 Status: {status}\n📝 Text: {msg}\n{e_GROUP} Groups: {n}"),
    },
    "ar_run": {"uz": "▶️ Ishga tushurish", "ru": "▶️ Запустить", "en": "▶️ Start"},
    "ar_replymsg": {"uz": "📝 Reply Matni", "ru": "📝 Текст ответа", "en": "📝 Reply text"},
    "ar_replygrp": {"uz": "👥 Reply Guruhlari", "ru": "👥 Группы ответа", "en": "👥 Reply groups"},
    "ar_dontsend": {"uz": "🚫 Yuborilmasin", "ru": "🚫 Не отправлять", "en": "🚫 Don't send"},
    "ar_settings": {"uz": "⚙️ AR: Sozlamalar", "ru": "⚙️ Настройки AR", "en": "⚙️ AR Settings"},
    "ar_send_text": {"uz": "📝 <b>Reply matni</b>\n\nKimdir guruhда sizni reply qilsa yuboriladigan javob:", "ru": "📝 <b>Текст ответа</b>\n\nОтвет когда вас reply в группе:", "en": "📝 <b>Reply text</b>\n\nReply when someone replies to you in a group:"},
    "ar_send_groups": {"uz": "👥 <b>Reply guruhlari</b>\n\nGuruh username larini yuboring (har birini yangi qatordan, @ bilan):", "ru": "👥 <b>Группы</b>\n\nОтправьте username групп (по одному на строку):", "en": "👥 <b>Reply groups</b>\n\nSend group usernames (one per line):"},

    # ═══ PRO ═══
    "pro_title": {"uz": "{e_CROWN} Pro tarif", "ru": "{e_CROWN} Pro тариф", "en": "{e_CROWN} Pro plan"},
    "pro_active": {"uz": "{e_CROWN} <b>Premium faol</b>", "ru": "{e_CROWN} <b>Premium активен</b>", "en": "{e_CROWN} <b>Premium active</b>"},
    "pro_free": {"uz": "Oddiy (bepul)", "ru": "Обычный", "en": "Free"},
    "pro_your": {"uz": "Tarifingiz", "ru": "Ваш тариф", "en": "Your plan"},
    "pro_feats": {
        "uz": "{e_OK} Cheksiz guruhlar\n{e_OK} Minimal interval\n{e_OK} Forward va tugmali xabar\n{e_OK} Bir nechta profil",
        "ru": "{e_OK} Без лимита групп\n{e_OK} Мин. интервал\n{e_OK} Forward и кнопки\n{e_OK} Много профилей",
        "en": "{e_OK} Unlimited groups\n{e_OK} Min interval\n{e_OK} Forward & buttons\n{e_OK} Multiple profiles",
    },
    "pro_gift_hint": {"uz": "{e_GIFT} Boshqaga ham sovg'a qila olasiz!", "ru": "{e_GIFT} Можно подарить другому!", "en": "{e_GIFT} You can gift it too!"},
    "b_pro_card": {"uz": "💳 Karta orqali", "ru": "💳 Картой", "en": "💳 By card"},
    "b_pro_stars": {"uz": "⭐️ Stars orqali", "ru": "⭐️ Через Stars", "en": "⭐️ Via Stars"},
    "b_pro_gift": {"uz": "🎁 Boshqaga sovg'a", "ru": "🎁 Подарить", "en": "🎁 Gift to someone"},
    "b_pro_admin": {"uz": "✉️ Murojat (admin)", "ru": "✉️ Связаться", "en": "✉️ Contact admin"},
    "pro_card_info": {
        "uz": ("{e_CARD} <b>Karta orqali to'lov</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
               "💳 <code>{card}</code>\n👤 {holder}\n💰 <b>{price}</b>\n\n"
               "1️⃣ Kartaga to'lang\n2️⃣ «To'ladim» bosing\n3️⃣ Admin tekshirib Pro beradi"),
        "ru": ("{e_CARD} <b>Оплата картой</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
               "💳 <code>{card}</code>\n👤 {holder}\n💰 <b>{price}</b>\n\n"
               "1️⃣ Оплатите\n2️⃣ Нажмите «Оплатил»\n3️⃣ Админ выдаст Pro"),
        "en": ("{e_CARD} <b>Card payment</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
               "💳 <code>{card}</code>\n👤 {holder}\n💰 <b>{price}</b>\n\n"
               "1️⃣ Pay\n2️⃣ Tap «Paid»\n3️⃣ Admin grants Pro"),
    },
    "no_card": {"uz": "Karta hali sozlanmagan. Admin bilan bog'laning.", "ru": "Карта не настроена.", "en": "Card not set up."},
    "b_paid": {"uz": "✅ To'ladim", "ru": "✅ Оплатил", "en": "✅ Paid"},
    "paid_sent": {"uz": "{e_OK} <b>So'rovingiz yuborildi!</b>\n\nAdmin tez orada Pro beradi.", "ru": "{e_OK} <b>Заявка отправлена!</b>\n\nАдмин скоро выдаст Pro.", "en": "{e_OK} <b>Request sent!</b>\n\nAdmin will grant Pro soon."},
    "gift_title": {"uz": "{e_GIFT} Boshqaga Pro sovg'a", "ru": "{e_GIFT} Подарить Pro", "en": "{e_GIFT} Gift Pro"},
    "gift_who": {
        "uz": "Kimga sovg'a qilmoqchisiz?\n\nUsername (@user) yoki ID raqamini yuboring.\n\n💡 <i>To'lovni siz qilasiz, Pro o'sha odamga beriladi.</i>",
        "ru": "Кому подарить?\n\nОтправьте @username или ID.\n\n💡 <i>Платите вы, Pro получает он.</i>",
        "en": "Gift to whom?\n\nSend @username or ID.\n\n💡 <i>You pay, they get Pro.</i>",
    },
    "gift_notfound": {"uz": "{e_WARN} Bu foydalanuvchi botda yo'q. U avval /start bosishi kerak.", "ru": "{e_WARN} Не найден. Пусть нажмёт /start.", "en": "{e_WARN} Not found. They must /start first."},
    "gift_confirm": {"uz": "{e_GIFT} <b>Sovg'a tasdig'i</b>\n\nKimga: <b>{name}</b>\n🆔 <code>{id}</code>\n💰 {price}\n\nTo'lov usulini tanlang:", "ru": "{e_GIFT} <b>Подтверждение</b>\n\nКому: <b>{name}</b>\n🆔 <code>{id}</code>\n💰 {price}\n\nСпособ оплаты:", "en": "{e_GIFT} <b>Confirm gift</b>\n\nTo: <b>{name}</b>\n🆔 <code>{id}</code>\n💰 {price}\n\nPayment method:"},
    "gift_sent": {"uz": "{e_OK} <b>Sovg'a yuborildi!</b>", "ru": "{e_OK} <b>Подарок отправлен!</b>", "en": "{e_OK} <b>Gift sent!</b>"},
    "gift_received": {"uz": "{e_GIFT} <b>Sizga sovg'a!</b>\n\n{name} sizga <b>Pro tarif</b> sovg'a qildi! 🎉", "ru": "{e_GIFT} <b>Вам подарок!</b>\n\n{name} подарил вам <b>Pro</b>! 🎉", "en": "{e_GIFT} <b>A gift for you!</b>\n\n{name} gifted you <b>Pro</b>! 🎉"},
    "pro_granted": {"uz": "{e_CROWN} <b>Tabriklaymiz!</b>\n\nPro tarif faollashtirildi! 🎉", "ru": "{e_CROWN} <b>Поздравляем!</b>\n\nPro активирован! 🎉", "en": "{e_CROWN} <b>Congrats!</b>\n\nPro activated! 🎉"},

    # ═══ YORDAM ═══
    "help_title": {"uz": "{e_USER} Yordam", "ru": "{e_USER} Помощь", "en": "{e_USER} Help"},
    "help_channel": {"uz": "Kanal", "ru": "Канал", "en": "Channel"},
    "help_chat": {"uz": "Chat", "ru": "Чат", "en": "Chat"},
    "help_admin": {"uz": "Admin", "ru": "Админ", "en": "Admin"},
    "help_contact": {"uz": "Savol yoki muammo bo'lsa <b>Murojat</b> tugmasini bosing.", "ru": "Вопрос? Нажмите <b>Связаться</b>.", "en": "Questions? Tap <b>Contact</b>."},
    "b_contact": {"uz": "✉️ Murojat", "ru": "✉️ Связаться", "en": "✉️ Contact"},
    "contact_q": {"uz": "✉️ Murojatingizni yozing (matn, rasm yoki video):", "ru": "✉️ Напишите обращение:", "en": "✉️ Write your message:"},
    "contact_sent": {"uz": "{e_OK} Murojatingiz adminга yuborildi! Tez orada javob beramiz.", "ru": "{e_OK} Отправлено админу! Скоро ответим.", "en": "{e_OK} Sent to admin! We'll reply soon."},

    # ═══ QO'LLANMA ═══
    "guide_title": {"uz": "{e_BOOK} Qo'llanma", "ru": "{e_BOOK} Руководство", "en": "{e_BOOK} Guide"},
    "guide_empty": {"uz": "Qo'llanma hali kiritilmagan.", "ru": "Руководство ещё не добавлено.", "en": "Guide not added yet."},

    # ═══ KALENDAR / TOOLS ═══
    "cal_title": {"uz": "{e_CALENDAR} Kalendar", "ru": "{e_CALENDAR} Календарь", "en": "{e_CALENDAR} Calendar"},
    "cal_soon": {"uz": "Jadval bo'yicha yuborish — tez orada.", "ru": "Расписание — скоро.", "en": "Scheduling — soon."},
    "tools_title": {"uz": "{e_TOOLS} Foydali funksiyalar", "ru": "{e_TOOLS} Полезное", "en": "{e_TOOLS} Tools"},

    # ═══ STATISTIKA (user) ═══
    "stat_title": {"uz": "{e_STATS} Statistika", "ru": "{e_STATS} Статистика", "en": "{e_STATS} Stats"},
    "stat_empty": {"uz": "Hali ma'lumot yo'q.", "ru": "Нет данных.", "en": "No data yet."},

    # ═══ ADMIN ═══
    "adm_title": {"uz": "{e_GEAR} <b>Admin panel</b>", "ru": "{e_GEAR} <b>Админ панель</b>", "en": "{e_GEAR} <b>Admin panel</b>"},
    "adm_noaccess": {"uz": "❌ Sizda admin huquqi yo'q.", "ru": "❌ Нет прав.", "en": "❌ No access."},
}


def t(key: str, lang: str = "uz", **kwargs) -> str:
    """Tarjima qaytaradi. Emoji {e_NAME} avtomatik almashtiriladi."""
    lang = lang if lang in ("uz", "ru", "en") else "uz"
    entry = TEXTS.get(key)
    if not entry:
        return key
    text = entry.get(lang) or entry.get("uz") or key
    # Emoji almashtirish: {e_ROCKET} -> premium emoji
    if "{e_" in text:
        import re
        def repl(m):
            return _em(m.group(1))
        text = re.sub(r"\{e_(\w+)\}", repl, text)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


def _strip_lead_emoji(text: str) -> str:
    """Matn boshidagi emoji prefiksini olib tashlaydi."""
    if not text:
        return text
    parts = text.split(" ", 1)
    if len(parts) == 2 and parts[0] and not any(c.isalnum() for c in parts[0]):
        return parts[1]
    return text


def is_button(text: str, key: str) -> bool:
    """
    Berilgan matn shu key ning biror tildagi varianti bilan mos keladimi?
    Emoji bo'lsin yoki bo'lmasin (ikkala holatда ham) tekshiradi.
    """
    if not text:
        return False
    variants = TEXTS.get(key, {})
    text_clean = _strip_lead_emoji(text).strip()
    for v in variants.values():
        if text == v:
            return True
        if text_clean == _strip_lead_emoji(v).strip():
            return True
    return False


# ═══ ADMIN PANEL reply tugmalari ═══
TEXTS.update({
    "adm_b_stats":    {"uz": "📊 Bot statistikasi", "ru": "📊 Статистика бота", "en": "📊 Bot stats"},
    "adm_b_users":    {"uz": "👥 Foydalanuvchilar", "ru": "👥 Пользователи", "en": "👥 Users"},
    "adm_b_give":     {"uz": "👑 Premium berish", "ru": "👑 Выдать Premium", "en": "👑 Give Premium"},
    "adm_b_take":     {"uz": "🚫 Premium olish", "ru": "🚫 Забрать Premium", "en": "🚫 Take Premium"},
    "adm_b_prices":   {"uz": "💰 Pro narxlari", "ru": "💰 Цены Pro", "en": "💰 Pro prices"},
    "adm_b_card":     {"uz": "💳 Karta raqami", "ru": "💳 Номер карты", "en": "💳 Card number"},
    "adm_b_guide":    {"uz": "📕 Qo'llanma matni", "ru": "📕 Текст руководства", "en": "📕 Guide text"},
    "adm_b_statsdesc":{"uz": "📈 Statistika tavsifi", "ru": "📈 Описание статистики", "en": "📈 Stats description"},
    "adm_b_help":     {"uz": "🎧 Yordam sozlash", "ru": "🎧 Настройка помощи", "en": "🎧 Help setup"},
    "adm_b_channels": {"uz": "📢 Majburiy obuna", "ru": "📢 Обяз. подписка", "en": "📢 Forced subs"},
    "adm_b_tickets":  {"uz": "📨 Murojatlar", "ru": "📨 Обращения", "en": "📨 Tickets"},
    "adm_b_broadcast":{"uz": "📣 Broadcast", "ru": "📣 Рассылка", "en": "📣 Broadcast"},
    "adm_b_exit":     {"uz": "🔙 Asosiy menyu", "ru": "🔙 Главное меню", "en": "🔙 Main menu"},
    "adm_panel_hint": {
        "uz": "Quyidagi tugmalardan kerakli bo'limni tanlang:",
        "ru": "Выберите нужный раздел:",
        "en": "Choose a section below:",
    },
})


# ═══ Akkaunt ulash qo'shimcha matnlar ═══
TEXTS.update({
    "accounts_title": {"uz": "{e_USERS} Akkauntlar", "ru": "{e_USERS} Аккаунты", "en": "{e_USERS} Accounts"},
    "qr_error": {"uz": "{e_WARN} QR yaratishda xato:", "ru": "{e_WARN} Ошибка QR:", "en": "{e_WARN} QR error:"},
    "need_2fa_title": {"uz": "🔐 <b>2FA parol kerak</b>\n\nAkkauntда ikki bosqichli himoya yoqilgan.\nParolingizni yuboring:",
                       "ru": "🔐 <b>Нужен 2FA пароль</b>\n\nВключена двухфакторная защита.\nОтправьте пароль:",
                       "en": "🔐 <b>2FA password needed</b>\n\nTwo-factor auth is enabled.\nSend your password:"},
    "error_generic": {"uz": "{e_WARN} Xato:", "ru": "{e_WARN} Ошибка:", "en": "{e_WARN} Error:"},
})


# ═══ Interval sekund matnlari ═══
TEXTS.update({
    "sec_set": {"uz": "✅ Interval {n} soniya o'rnatildi!", "ru": "✅ Интервал {n} сек!", "en": "✅ Interval set to {n} sec!"},
    "sec_range": {"uz": "{e_WARN} Soniya 1 — 3600 oralig'ida bo'lsin.", "ru": "{e_WARN} Секунды 1 — 3600.", "en": "{e_WARN} Seconds 1 — 3600."},
    "sec_pro_only": {"uz": "🔒 Soniyalik interval faqat Pro tarifda! (juda tez yuborish)", "ru": "🔒 Интервал в секундах только в Pro!", "en": "🔒 Seconds interval is Pro only!"},
    "int_manual_q2": {
        "uz": ("{e_EDIT} <b>Qo'lda interval kiritish</b>\n\n"
               "• Daqiqa uchun son: <code>25</code> (25 daqiqa)\n"
               "• Soniya uchun nuqta bilan: <code>.5</code> (5 soniya), <code>.30</code> (30 soniya)\n\n"
               "<i>Soniyalik interval faqat Pro tarifda.</i>"),
        "ru": ("{e_EDIT} <b>Ручной ввод интервала</b>\n\n"
               "• Минуты: <code>25</code> (25 минут)\n"
               "• Секунды с точкой: <code>.5</code> (5 сек), <code>.30</code> (30 сек)\n\n"
               "<i>Секунды только в Pro.</i>"),
        "en": ("{e_EDIT} <b>Manual interval</b>\n\n"
               "• Minutes: <code>25</code> (25 min)\n"
               "• Seconds with dot: <code>.5</code> (5 sec), <code>.30</code> (30 sec)\n\n"
               "<i>Seconds interval is Pro only.</i>"),
    },
})


def fmt_interval(interval_min: int, interval_sec: int, lang: str = "uz") -> str:
    """Intervalni chiroyli ko'rsatadi (sekund yoki daqiqa)."""
    if interval_sec and interval_sec > 0:
        unit = "soniya" if lang == "uz" else "сек" if lang == "ru" else "sec"
        return f"{interval_sec} {unit}"
    unit = "daqiqa" if lang == "uz" else "мин" if lang == "ru" else "min"
    return f"{interval_min} {unit}"
