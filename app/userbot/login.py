"""
Userbot akkauntini ulash — QR kod (asosiy) va SMS (muqobil).

QR ulash oqimi (Telethon qr_login):
  1. client.qr_login() chaqiriladi → URL keladi
  2. URL'dan QR rasm yasaladi va foydalanuvchiga yuboriladi
  3. Foydalanuvchi Telegram → Sozlamalar → Qurilmalar → QR skaner qiladi
  4. qr.wait() login tugaganini kutadi
  5. Agar 2FA (parol) bo'lsa — alohida so'raladi

SMS ulash oqimi:
  1. client.send_code_request(phone) → kod yuboriladi
  2. Foydalanuvchi kodni kiritadi
  3. client.sign_in(phone, code)
  4. 2FA bo'lsa — parol so'raladi
"""
import asyncio
import io
from dataclasses import dataclass, field
from typing import Optional

import qrcode
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    PasswordHashInvalidError,
)

from app.config import config


# ─── Vaqtinchalik ulash sessiyalari (xotirada) ──────────────────────
@dataclass
class PendingLogin:
    """Foydalanuvchi ulash jarayonida — vaqtinchalik holat."""
    owner_id: int
    client: TelegramClient
    method: str = "qr"            # "qr" yoki "sms"
    phone: str = ""
    phone_code_hash: str = ""
    qr_task: Optional[asyncio.Task] = None
    needs_password: bool = False


# owner_id → PendingLogin
_pending: dict[int, PendingLogin] = {}


def _new_client() -> TelegramClient:
    """Yangi StringSession bilan Telethon klienti."""
    return TelegramClient(
        StringSession(),
        config.api_id,
        config.api_hash,
        device_model="Auto Habar Pro",
        system_version="1.0",
        app_version="1.0",
    )


def make_qr_image(url: str) -> io.BytesIO:
    """QR URL'dan PNG rasm (xotirada) yasaydi."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    buf.name = "qr.png"
    img.save(buf, "PNG")
    buf.seek(0)
    return buf


# ═══════════════════════════════════════════════════════════════════
# QR ULASH
# ═══════════════════════════════════════════════════════════════════

async def start_qr_login(owner_id: int) -> tuple[io.BytesIO, "qr"]:
    """
    QR loginni boshlaydi. QR rasm va qr-login obyektini qaytaradi.
    """
    # Avvalgi ulashni tozalash
    await cancel_login(owner_id)

    client = _new_client()
    await client.connect()

    qr = await client.qr_login()
    img = make_qr_image(qr.url)

    _pending[owner_id] = PendingLogin(
        owner_id=owner_id, client=client, method="qr",
    )
    return img, qr


async def wait_qr_result(owner_id: int, qr, timeout: int = 60) -> dict:
    """
    QR skaner qilinishini kutadi.

    Returns:
        {"status": "ok", "account": {...}}        — muvaffaqiyat
        {"status": "password"}                    — 2FA parol kerak
        {"status": "timeout"}                     — vaqt tugadi
        {"status": "error", "message": "..."}     — xato
    """
    pend = _pending.get(owner_id)
    if not pend:
        return {"status": "error", "message": "Sessiya topilmadi"}

    try:
        await asyncio.wait_for(qr.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        return {"status": "timeout"}
    except SessionPasswordNeededError:
        pend.needs_password = True
        return {"status": "password"}
    except Exception as e:
        return {"status": "error", "message": str(e)[:200]}

    # Login muvaffaqiyatli — akkaunt ma'lumotlarini olamiz
    return await _finalize(owner_id)


# ═══════════════════════════════════════════════════════════════════
# SMS ULASH
# ═══════════════════════════════════════════════════════════════════

async def start_sms_login(owner_id: int, phone: str) -> dict:
    """
    Telefon raqamiga kod yuboradi.
    Returns: {"status": "code_sent"} | {"status": "error", "message": ...}
    """
    await cancel_login(owner_id)

    client = _new_client()
    await client.connect()

    try:
        sent = await client.send_code_request(phone)
    except PhoneNumberInvalidError:
        await client.disconnect()
        return {"status": "error", "message": "Telefon raqami noto'g'ri"}
    except Exception as e:
        await client.disconnect()
        return {"status": "error", "message": str(e)[:200]}

    _pending[owner_id] = PendingLogin(
        owner_id=owner_id, client=client, method="sms",
        phone=phone, phone_code_hash=sent.phone_code_hash,
    )
    return {"status": "code_sent"}


async def submit_sms_code(owner_id: int, code: str) -> dict:
    """
    SMS kodni tekshiradi.
    Returns:
        {"status": "ok", "account": {...}}
        {"status": "password"}                — 2FA kerak
        {"status": "error", "message": ...}
    """
    pend = _pending.get(owner_id)
    if not pend or pend.method != "sms":
        return {"status": "error", "message": "Sessiya topilmadi. Qaytadan boshlang."}

    try:
        await pend.client.sign_in(
            phone=pend.phone,
            code=code.strip(),
            phone_code_hash=pend.phone_code_hash,
        )
    except PhoneCodeInvalidError:
        return {"status": "error", "message": "Kod noto'g'ri. Qayta kiriting."}
    except SessionPasswordNeededError:
        pend.needs_password = True
        return {"status": "password"}
    except Exception as e:
        return {"status": "error", "message": str(e)[:200]}

    return await _finalize(owner_id)


# ═══════════════════════════════════════════════════════════════════
# 2FA PAROL (QR va SMS uchun umumiy)
# ═══════════════════════════════════════════════════════════════════

async def submit_password(owner_id: int, password: str) -> dict:
    """
    2FA parolni tekshiradi.
    Returns: {"status": "ok", "account": {...}} | {"status": "error", ...}
    """
    pend = _pending.get(owner_id)
    if not pend:
        return {"status": "error", "message": "Sessiya topilmadi"}

    try:
        await pend.client.sign_in(password=password.strip())
    except (PasswordHashInvalidError, PhoneCodeInvalidError):
        return {"status": "error", "message": "Parol noto'g'ri. Qayta kiriting."}
    except Exception as e:
        return {"status": "error", "message": str(e)[:200]}

    return await _finalize(owner_id)


# ═══════════════════════════════════════════════════════════════════
# YAKUNLASH — sessiyani saqlash
# ═══════════════════════════════════════════════════════════════════

async def _finalize(owner_id: int) -> dict:
    """Login tugagach: me() ma'lumotlarini olib, session_string qaytaradi."""
    pend = _pending.get(owner_id)
    if not pend:
        return {"status": "error", "message": "Sessiya topilmadi"}

    try:
        me = await pend.client.get_me()
        session_string = pend.client.session.save()
        account = {
            "tg_id": me.id,
            "name": " ".join(filter(None, [me.first_name, me.last_name])) or "Akkaunt",
            "username": me.username or "",
            "phone": me.phone or pend.phone,
            "session_string": session_string,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)[:200]}
    finally:
        # Ulash klientini uzamiz (saqlangan sessiya keyin qayta ishlatiladi)
        try:
            await pend.client.disconnect()
        except Exception:
            pass
        _pending.pop(owner_id, None)

    return {"status": "ok", "account": account}


async def cancel_login(owner_id: int) -> None:
    """Davom etayotgan ulashni bekor qiladi."""
    pend = _pending.pop(owner_id, None)
    if pend:
        if pend.qr_task and not pend.qr_task.done():
            pend.qr_task.cancel()
        try:
            await pend.client.disconnect()
        except Exception:
            pass


def has_pending(owner_id: int) -> bool:
    return owner_id in _pending


def get_pending(owner_id: int) -> Optional[PendingLogin]:
    return _pending.get(owner_id)
