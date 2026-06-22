"""
Bot sozlamalari — .env faylidan o'qiladi.
"""
import os
from dataclasses import dataclass, field

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _env(key: str, default: str = "") -> str:
    val = os.getenv(key, default)
    return val.strip() if val else default


def _env_int(key: str, default: int = 0) -> int:
    try:
        return int(_env(key, str(default)))
    except (ValueError, TypeError):
        return default


def _admin_ids() -> list[int]:
    raw = _env("ADMIN_IDS", "")
    out = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            out.append(int(part))
    return out


@dataclass
class Config:
    # ─── Telegram Bot ─────────────────────────────────
    bot_token: str = field(default_factory=lambda: _env("BOT_TOKEN"))
    bot_username: str = field(default_factory=lambda: _env("BOT_USERNAME", "AutoHabarProBot"))

    # ─── Telethon (userbot) — my.telegram.org dan ─────
    api_id: int = field(default_factory=lambda: _env_int("TG_API_ID"))
    api_hash: str = field(default_factory=lambda: _env("TG_API_HASH"))

    # ─── Admin ────────────────────────────────────────
    admin_ids: list[int] = field(default_factory=_admin_ids)
    admin_username: str = field(default_factory=lambda: _env("ADMIN_USERNAME", "admin"))

    # ─── PostgreSQL ───────────────────────────────────
    db_host: str = field(default_factory=lambda: _env("DB_HOST", "localhost"))
    db_port: int = field(default_factory=lambda: _env_int("DB_PORT", 5432))
    db_name: str = field(default_factory=lambda: _env("DB_NAME", "autohabar"))
    db_user: str = field(default_factory=lambda: _env("DB_USER", "postgres"))
    db_pass: str = field(default_factory=lambda: _env("DB_PASS", ""))

    # ─── Sessions papkasi ─────────────────────────────
    sessions_dir: str = field(default_factory=lambda: _env("SESSIONS_DIR", "sessions"))

    # ─── Tarif limitleri ──────────────────────────────
    free_max_groups: int = field(default_factory=lambda: _env_int("FREE_MAX_GROUPS", 10))
    free_min_interval: int = field(default_factory=lambda: _env_int("FREE_MIN_INTERVAL", 5))  # daqiqa

    @property
    def dsn(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admin_ids


config = Config()
