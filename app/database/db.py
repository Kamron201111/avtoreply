"""
PostgreSQL ma'lumotlar bazasi qatlami (asyncpg).
Jadvallar: users, accounts, groups, settings, broadcast_log, autoreplies
"""
import asyncpg
import json
from datetime import datetime
from typing import Optional, Any

from app.config import config

_pool: Optional[asyncpg.Pool] = None


async def init_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            host=config.db_host,
            port=config.db_port,
            database=config.db_name,
            user=config.db_user,
            password=config.db_pass,
            min_size=2,
            max_size=10,
            command_timeout=60,
        )
        await _create_tables()
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


def pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("DB pool ishga tushmagan. init_pool() chaqiring.")
    return _pool


# ═══════════════════════════════════════════════════════════════════
# JADVALLAR
# ═══════════════════════════════════════════════════════════════════

async def _create_tables() -> None:
    async with _pool.acquire() as con:
        await con.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id           SERIAL PRIMARY KEY,
                telegram_id  BIGINT UNIQUE NOT NULL,
                username     TEXT NOT NULL DEFAULT '',
                full_name    TEXT NOT NULL DEFAULT '',
                is_premium   BOOLEAN NOT NULL DEFAULT FALSE,
                is_banned    BOOLEAN NOT NULL DEFAULT FALSE,
                lang         TEXT NOT NULL DEFAULT 'uz',
                created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                last_seen    TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)

        # Ulangan userbot akkauntlari
        await con.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id              SERIAL PRIMARY KEY,
                owner_id        BIGINT NOT NULL,
                phone           TEXT NOT NULL DEFAULT '',
                account_tg_id   BIGINT,
                account_name    TEXT NOT NULL DEFAULT '',
                account_username TEXT NOT NULL DEFAULT '',
                session_string  TEXT NOT NULL DEFAULT '',
                is_active       BOOLEAN NOT NULL DEFAULT FALSE,
                created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE (owner_id, account_tg_id)
            );
        """)

        # Avto-xabar yuboriladigan guruhlar
        await con.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id          SERIAL PRIMARY KEY,
                account_id  INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                chat_id     BIGINT NOT NULL,
                title       TEXT NOT NULL DEFAULT '',
                is_enabled  BOOLEAN NOT NULL DEFAULT TRUE,
                added_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE (account_id, chat_id)
            );
        """)

        # Har bir akkauntning avto-xabar sozlamalari
        await con.execute("""
            CREATE TABLE IF NOT EXISTS autosend (
                account_id      INTEGER PRIMARY KEY REFERENCES accounts(id) ON DELETE CASCADE,
                message_type    TEXT NOT NULL DEFAULT 'text',
                message_text    TEXT NOT NULL DEFAULT '',
                message_file_id TEXT NOT NULL DEFAULT '',
                interval_min    INTEGER NOT NULL DEFAULT 5,
                is_running      BOOLEAN NOT NULL DEFAULT FALSE,
                last_sent_at    TIMESTAMPTZ,
                next_send_at    TIMESTAMPTZ,
                mention_enabled BOOLEAN NOT NULL DEFAULT FALSE,
                auto_delete_sec INTEGER NOT NULL DEFAULT 0,
                buttons_json    TEXT NOT NULL DEFAULT '[]'
            );
        """)

        # Autoreply — DM avtomatik javob
        await con.execute("""
            CREATE TABLE IF NOT EXISTS autoreplies (
                account_id   INTEGER PRIMARY KEY REFERENCES accounts(id) ON DELETE CASCADE,
                is_enabled   BOOLEAN NOT NULL DEFAULT FALSE,
                reply_text   TEXT NOT NULL DEFAULT '',
                only_offline BOOLEAN NOT NULL DEFAULT TRUE,
                updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)

        # Statistika logi
        await con.execute("""
            CREATE TABLE IF NOT EXISTS send_log (
                id          SERIAL PRIMARY KEY,
                account_id  INTEGER NOT NULL,
                chat_id     BIGINT NOT NULL,
                status      TEXT NOT NULL DEFAULT 'sent',
                error       TEXT NOT NULL DEFAULT '',
                sent_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)

        # Global sozlamalar (kalit-qiymat)
        await con.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL DEFAULT ''
            );
        """)


# ═══════════════════════════════════════════════════════════════════
# FOYDALANUVCHILAR
# ═══════════════════════════════════════════════════════════════════

async def get_or_create_user(tg_id: int, username: str, full_name: str) -> asyncpg.Record:
    async with pool().acquire() as con:
        row = await con.fetchrow("SELECT * FROM users WHERE telegram_id=$1", tg_id)
        if row:
            await con.execute(
                "UPDATE users SET username=$1, full_name=$2, last_seen=NOW() WHERE telegram_id=$3",
                username, full_name, tg_id,
            )
            return await con.fetchrow("SELECT * FROM users WHERE telegram_id=$1", tg_id)
        return await con.fetchrow(
            """INSERT INTO users (telegram_id, username, full_name)
               VALUES ($1,$2,$3) RETURNING *""",
            tg_id, username, full_name,
        )


async def get_user(tg_id: int) -> Optional[asyncpg.Record]:
    async with pool().acquire() as con:
        return await con.fetchrow("SELECT * FROM users WHERE telegram_id=$1", tg_id)


async def all_users() -> list[asyncpg.Record]:
    async with pool().acquire() as con:
        return await con.fetch("SELECT * FROM users ORDER BY id")


async def set_banned(tg_id: int, banned: bool) -> None:
    async with pool().acquire() as con:
        await con.execute("UPDATE users SET is_banned=$1 WHERE telegram_id=$2", banned, tg_id)


async def set_premium(tg_id: int, premium: bool) -> None:
    async with pool().acquire() as con:
        await con.execute("UPDATE users SET is_premium=$1 WHERE telegram_id=$2", premium, tg_id)


# ═══════════════════════════════════════════════════════════════════
# AKKAUNTLAR (userbot)
# ═══════════════════════════════════════════════════════════════════

async def create_account(owner_id: int, account_tg_id: int, name: str,
                         username: str, phone: str, session_string: str) -> asyncpg.Record:
    async with pool().acquire() as con:
        row = await con.fetchrow(
            """INSERT INTO accounts
                 (owner_id, account_tg_id, account_name, account_username, phone, session_string, is_active)
               VALUES ($1,$2,$3,$4,$5,$6,TRUE)
               ON CONFLICT (owner_id, account_tg_id)
               DO UPDATE SET session_string=$6, account_name=$3,
                             account_username=$4, phone=$5, is_active=TRUE
               RETURNING *""",
            owner_id, account_tg_id, name, username, phone, session_string,
        )
        # autosend va autoreply standart yozuvlarini yaratish
        await con.execute(
            "INSERT INTO autosend (account_id) VALUES ($1) ON CONFLICT DO NOTHING", row["id"]
        )
        await con.execute(
            "INSERT INTO autoreplies (account_id) VALUES ($1) ON CONFLICT DO NOTHING", row["id"]
        )
        return row


async def get_accounts(owner_id: int) -> list[asyncpg.Record]:
    async with pool().acquire() as con:
        return await con.fetch(
            "SELECT * FROM accounts WHERE owner_id=$1 ORDER BY id", owner_id
        )


async def get_account(account_id: int) -> Optional[asyncpg.Record]:
    async with pool().acquire() as con:
        return await con.fetchrow("SELECT * FROM accounts WHERE id=$1", account_id)


async def get_active_accounts() -> list[asyncpg.Record]:
    """Avto-yuborish ishlab turgan barcha akkauntlar."""
    async with pool().acquire() as con:
        return await con.fetch("""
            SELECT a.*, s.interval_min, s.message_type, s.message_text,
                   s.message_file_id, s.is_running, s.next_send_at,
                   s.mention_enabled, s.auto_delete_sec, s.buttons_json
            FROM accounts a
            JOIN autosend s ON s.account_id = a.id
            WHERE a.is_active = TRUE AND s.is_running = TRUE
        """)


async def delete_account(account_id: int) -> None:
    async with pool().acquire() as con:
        await con.execute("DELETE FROM accounts WHERE id=$1", account_id)


# ═══════════════════════════════════════════════════════════════════
# GURUHLAR
# ═══════════════════════════════════════════════════════════════════

async def add_group(account_id: int, chat_id: int, title: str) -> bool:
    async with pool().acquire() as con:
        try:
            await con.execute(
                """INSERT INTO groups (account_id, chat_id, title)
                   VALUES ($1,$2,$3)
                   ON CONFLICT (account_id, chat_id) DO UPDATE SET title=$3""",
                account_id, chat_id, title,
            )
            return True
        except Exception:
            return False


async def get_groups(account_id: int) -> list[asyncpg.Record]:
    async with pool().acquire() as con:
        return await con.fetch(
            "SELECT * FROM groups WHERE account_id=$1 ORDER BY id", account_id
        )


async def get_enabled_groups(account_id: int) -> list[asyncpg.Record]:
    async with pool().acquire() as con:
        return await con.fetch(
            "SELECT * FROM groups WHERE account_id=$1 AND is_enabled=TRUE", account_id
        )


async def remove_group(group_id: int) -> None:
    async with pool().acquire() as con:
        await con.execute("DELETE FROM groups WHERE id=$1", group_id)


async def count_groups(account_id: int) -> int:
    async with pool().acquire() as con:
        return await con.fetchval(
            "SELECT COUNT(*) FROM groups WHERE account_id=$1", account_id
        )


# ═══════════════════════════════════════════════════════════════════
# AVTO-YUBORISH SOZLAMALARI
# ═══════════════════════════════════════════════════════════════════

async def get_autosend(account_id: int) -> Optional[asyncpg.Record]:
    async with pool().acquire() as con:
        return await con.fetchrow("SELECT * FROM autosend WHERE account_id=$1", account_id)


async def update_autosend(account_id: int, **fields) -> None:
    if not fields:
        return
    cols = ", ".join(f"{k}=${i+2}" for i, k in enumerate(fields))
    vals = list(fields.values())
    async with pool().acquire() as con:
        await con.execute(
            f"UPDATE autosend SET {cols} WHERE account_id=$1", account_id, *vals
        )


async def set_running(account_id: int, running: bool, next_send_at: datetime = None) -> None:
    async with pool().acquire() as con:
        await con.execute(
            "UPDATE autosend SET is_running=$1, next_send_at=$2 WHERE account_id=$3",
            running, next_send_at, account_id,
        )


# ═══════════════════════════════════════════════════════════════════
# AUTOREPLY
# ═══════════════════════════════════════════════════════════════════

async def get_autoreply(account_id: int) -> Optional[asyncpg.Record]:
    async with pool().acquire() as con:
        return await con.fetchrow("SELECT * FROM autoreplies WHERE account_id=$1", account_id)


async def update_autoreply(account_id: int, **fields) -> None:
    if not fields:
        return
    cols = ", ".join(f"{k}=${i+2}" for i, k in enumerate(fields))
    vals = list(fields.values())
    async with pool().acquire() as con:
        await con.execute(
            f"UPDATE autoreplies SET {cols}, updated_at=NOW() WHERE account_id=$1",
            account_id, *vals,
        )


# ═══════════════════════════════════════════════════════════════════
# STATISTIKA
# ═══════════════════════════════════════════════════════════════════

async def log_send(account_id: int, chat_id: int, status: str, error: str = "") -> None:
    async with pool().acquire() as con:
        await con.execute(
            """INSERT INTO send_log (account_id, chat_id, status, error)
               VALUES ($1,$2,$3,$4)""",
            account_id, chat_id, status, error,
        )


async def get_stats(account_id: int) -> dict:
    async with pool().acquire() as con:
        total = await con.fetchval(
            "SELECT COUNT(*) FROM send_log WHERE account_id=$1", account_id
        )
        sent = await con.fetchval(
            "SELECT COUNT(*) FROM send_log WHERE account_id=$1 AND status='sent'", account_id
        )
        failed = await con.fetchval(
            "SELECT COUNT(*) FROM send_log WHERE account_id=$1 AND status='failed'", account_id
        )
        today = await con.fetchval(
            """SELECT COUNT(*) FROM send_log
               WHERE account_id=$1 AND status='sent' AND sent_at::date = CURRENT_DATE""",
            account_id,
        )
    return {"total": total, "sent": sent, "failed": failed, "today": today}


async def get_global_stats() -> dict:
    async with pool().acquire() as con:
        users = await con.fetchval("SELECT COUNT(*) FROM users")
        accounts = await con.fetchval("SELECT COUNT(*) FROM accounts")
        active = await con.fetchval("SELECT COUNT(*) FROM autosend WHERE is_running=TRUE")
        groups = await con.fetchval("SELECT COUNT(*) FROM groups")
        sent_total = await con.fetchval("SELECT COUNT(*) FROM send_log WHERE status='sent'")
    return {
        "users": users, "accounts": accounts,
        "active": active, "groups": groups, "sent_total": sent_total,
    }


# ═══════════════════════════════════════════════════════════════════
# GLOBAL SOZLAMALAR
# ═══════════════════════════════════════════════════════════════════

async def get_setting(key: str, default: str = "") -> str:
    async with pool().acquire() as con:
        val = await con.fetchval("SELECT value FROM settings WHERE key=$1", key)
        return val if val is not None else default


async def set_setting(key: str, value: str) -> None:
    async with pool().acquire() as con:
        await con.execute(
            """INSERT INTO settings (key, value) VALUES ($1,$2)
               ON CONFLICT (key) DO UPDATE SET value=$2""",
            key, value,
        )
