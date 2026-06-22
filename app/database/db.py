"""
PostgreSQL ma'lumotlar bazasi qatlami (asyncpg).
"""
import asyncpg
from datetime import datetime
from typing import Optional

from app.config import config

_pool: Optional[asyncpg.Pool] = None


async def init_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            host=config.db_host, port=config.db_port, database=config.db_name,
            user=config.db_user, password=config.db_pass,
            min_size=2, max_size=10, command_timeout=60,
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
        raise RuntimeError("DB pool ishga tushmagan.")
    return _pool


async def _create_tables() -> None:
    async with _pool.acquire() as con:
        await con.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGSERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username TEXT NOT NULL DEFAULT '',
                full_name TEXT NOT NULL DEFAULT '',
                lang TEXT NOT NULL DEFAULT '',
                is_premium BOOLEAN NOT NULL DEFAULT FALSE,
                is_banned BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                last_seen TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        # account_tg_id GLOBAL UNIQUE — bitta akkaunt faqat bir marta ulanadi
        await con.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id BIGSERIAL PRIMARY KEY,
                owner_id BIGINT NOT NULL,
                phone TEXT NOT NULL DEFAULT '',
                account_tg_id BIGINT UNIQUE,
                account_name TEXT NOT NULL DEFAULT '',
                account_username TEXT NOT NULL DEFAULT '',
                session_string TEXT NOT NULL DEFAULT '',
                is_active BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        await con.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id BIGSERIAL PRIMARY KEY,
                account_id BIGINT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                chat_id BIGINT NOT NULL,
                title TEXT NOT NULL DEFAULT '',
                is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
                added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE (account_id, chat_id)
            );
        """)
        await con.execute("""
            CREATE TABLE IF NOT EXISTS autosend (
                account_id BIGINT PRIMARY KEY REFERENCES accounts(id) ON DELETE CASCADE,
                message_type TEXT NOT NULL DEFAULT 'text',
                message_text TEXT NOT NULL DEFAULT '',
                message_file_id TEXT NOT NULL DEFAULT '',
                interval_min INTEGER NOT NULL DEFAULT 5,
                is_running BOOLEAN NOT NULL DEFAULT FALSE,
                last_sent_at TIMESTAMPTZ,
                next_send_at TIMESTAMPTZ,
                mention_enabled BOOLEAN NOT NULL DEFAULT FALSE,
                auto_delete_sec INTEGER NOT NULL DEFAULT 0,
                cycles INTEGER NOT NULL DEFAULT 0
            );
        """)
        # Autoreply (DM Javob — onlayn bo'lmaganda DM ga javob)
        await con.execute("""
            CREATE TABLE IF NOT EXISTS dm_reply (
                account_id BIGINT PRIMARY KEY REFERENCES accounts(id) ON DELETE CASCADE,
                is_enabled BOOLEAN NOT NULL DEFAULT FALSE,
                reply_text TEXT NOT NULL DEFAULT '',
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        # Group reply (guruhda reply qilinsa javob)
        await con.execute("""
            CREATE TABLE IF NOT EXISTS group_reply (
                account_id BIGINT PRIMARY KEY REFERENCES accounts(id) ON DELETE CASCADE,
                is_enabled BOOLEAN NOT NULL DEFAULT FALSE,
                reply_text TEXT NOT NULL DEFAULT '',
                groups_json TEXT NOT NULL DEFAULT '[]',
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        await con.execute("""
            CREATE TABLE IF NOT EXISTS send_log (
                id BIGSERIAL PRIMARY KEY,
                account_id BIGINT NOT NULL,
                chat_id BIGINT NOT NULL,
                status TEXT NOT NULL DEFAULT 'sent',
                error TEXT NOT NULL DEFAULT '',
                sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        # Majburiy obuna kanallari
        await con.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id BIGSERIAL PRIMARY KEY,
                channel_id TEXT NOT NULL,
                title TEXT NOT NULL DEFAULT '',
                invite_url TEXT NOT NULL DEFAULT '',
                added_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        # Murojat (support) — ikki tomonlama
        await con.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                username TEXT NOT NULL DEFAULT '',
                message TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'open',
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        await con.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL DEFAULT ''
            );
        """)

        # ─── MIGRATION: eski jadvallarga yetishmayotgan ustunlarni qo'shish ───
        await _migrate(con)


async def _migrate(con) -> None:
    """Eski DB'ga yangi ustunlarni xavfsiz qo'shadi (ADD COLUMN IF NOT EXISTS)."""
    migrations = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS lang TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE autosend ADD COLUMN IF NOT EXISTS cycles INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE autosend ADD COLUMN IF NOT EXISTS mention_enabled BOOLEAN NOT NULL DEFAULT FALSE",
        "ALTER TABLE autosend ADD COLUMN IF NOT EXISTS auto_delete_sec INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS account_username TEXT NOT NULL DEFAULT ''",
    ]
    for sql in migrations:
        try:
            await con.execute(sql)
        except Exception as e:
            print(f"[migration] {sql[:50]}... xato: {e}")

    # account_tg_id ni GLOBAL UNIQUE qilish (agar eski (owner_id, account_tg_id) bo'lsa)
    try:
        # Eski composite unique constraintni o'chiramiz (agar bor bo'lsa)
        await con.execute("""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname='accounts_owner_id_account_tg_id_key') THEN
                    ALTER TABLE accounts DROP CONSTRAINT accounts_owner_id_account_tg_id_key;
                END IF;
            END $$;
        """)
    except Exception as e:
        print(f"[migration] drop old constraint: {e}")
    # account_tg_id ga UNIQUE qo'shish (agar yo'q bo'lsa)
    try:
        await con.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='accounts_account_tg_id_key') THEN
                    ALTER TABLE accounts ADD CONSTRAINT accounts_account_tg_id_key UNIQUE (account_tg_id);
                END IF;
            END $$;
        """)
    except Exception as e:
        print(f"[migration] add unique: {e}")

    # dm_reply va group_reply jadvallari mavjud akkauntlar uchun yozuv yaratish
    try:
        await con.execute("""
            INSERT INTO dm_reply (account_id)
            SELECT id FROM accounts WHERE id NOT IN (SELECT account_id FROM dm_reply)
        """)
        await con.execute("""
            INSERT INTO group_reply (account_id)
            SELECT id FROM accounts WHERE id NOT IN (SELECT account_id FROM group_reply)
        """)
        await con.execute("""
            INSERT INTO autosend (account_id)
            SELECT id FROM accounts WHERE id NOT IN (SELECT account_id FROM autosend)
        """)
    except Exception as e:
        print(f"[migration] backfill reply rows: {e}")


# ═══ USERS ══════════════════════════════════════════════════════════
async def get_or_create_user(tg_id, username, full_name):
    async with pool().acquire() as con:
        row = await con.fetchrow("SELECT * FROM users WHERE telegram_id=$1", tg_id)
        if row:
            await con.execute(
                "UPDATE users SET username=$1, full_name=$2, last_seen=NOW() WHERE telegram_id=$3",
                username, full_name, tg_id)
            return await con.fetchrow("SELECT * FROM users WHERE telegram_id=$1", tg_id)
        return await con.fetchrow(
            "INSERT INTO users (telegram_id, username, full_name) VALUES ($1,$2,$3) RETURNING *",
            tg_id, username, full_name)


async def get_user(tg_id):
    async with pool().acquire() as con:
        return await con.fetchrow("SELECT * FROM users WHERE telegram_id=$1", tg_id)


async def all_users():
    async with pool().acquire() as con:
        return await con.fetch("SELECT * FROM users ORDER BY id")


async def set_lang(tg_id, lang):
    async with pool().acquire() as con:
        await con.execute("UPDATE users SET lang=$1 WHERE telegram_id=$2", lang, tg_id)


async def set_banned(tg_id, banned):
    async with pool().acquire() as con:
        await con.execute("UPDATE users SET is_banned=$1 WHERE telegram_id=$2", banned, tg_id)


async def set_premium(tg_id, premium):
    async with pool().acquire() as con:
        await con.execute("UPDATE users SET is_premium=$1 WHERE telegram_id=$2", premium, tg_id)


# ═══ ACCOUNTS ═══════════════════════════════════════════════════════
async def account_exists(account_tg_id) -> Optional[asyncpg.Record]:
    """Bu Telegram akkaunt allaqachon ulanganmi (global)?"""
    async with pool().acquire() as con:
        return await con.fetchrow("SELECT * FROM accounts WHERE account_tg_id=$1", account_tg_id)


async def create_account(owner_id, account_tg_id, name, username, phone, session_string):
    async with pool().acquire() as con:
        row = await con.fetchrow(
            """INSERT INTO accounts
                 (owner_id, account_tg_id, account_name, account_username, phone, session_string, is_active)
               VALUES ($1,$2,$3,$4,$5,$6,TRUE)
               ON CONFLICT (account_tg_id)
               DO UPDATE SET owner_id=$1, session_string=$6, account_name=$3,
                             account_username=$4, phone=$5, is_active=TRUE
               RETURNING *""",
            owner_id, account_tg_id, name, username, phone, session_string)
        await con.execute("INSERT INTO autosend (account_id) VALUES ($1) ON CONFLICT DO NOTHING", row["id"])
        await con.execute("INSERT INTO dm_reply (account_id) VALUES ($1) ON CONFLICT DO NOTHING", row["id"])
        await con.execute("INSERT INTO group_reply (account_id) VALUES ($1) ON CONFLICT DO NOTHING", row["id"])
        return row


async def get_accounts(owner_id):
    async with pool().acquire() as con:
        return await con.fetch("SELECT * FROM accounts WHERE owner_id=$1 ORDER BY id", owner_id)


async def get_account(account_id):
    async with pool().acquire() as con:
        return await con.fetchrow("SELECT * FROM accounts WHERE id=$1", account_id)


async def get_active_accounts():
    async with pool().acquire() as con:
        return await con.fetch("""
            SELECT a.*, s.interval_min, s.message_type, s.message_text, s.message_file_id,
                   s.is_running, s.next_send_at, s.mention_enabled, s.auto_delete_sec, s.cycles
            FROM accounts a JOIN autosend s ON s.account_id=a.id
            WHERE a.is_active=TRUE AND s.is_running=TRUE
        """)


async def delete_account(account_id):
    async with pool().acquire() as con:
        await con.execute("DELETE FROM accounts WHERE id=$1", account_id)


async def count_accounts():
    async with pool().acquire() as con:
        return await con.fetchval("SELECT COUNT(*) FROM accounts")


# ═══ GROUPS ═════════════════════════════════════════════════════════
async def add_group(account_id, chat_id, title):
    async with pool().acquire() as con:
        try:
            await con.execute(
                """INSERT INTO groups (account_id, chat_id, title) VALUES ($1,$2,$3)
                   ON CONFLICT (account_id, chat_id) DO UPDATE SET title=$3""",
                account_id, chat_id, title)
            return True
        except Exception:
            return False


async def get_groups(account_id):
    async with pool().acquire() as con:
        return await con.fetch("SELECT * FROM groups WHERE account_id=$1 ORDER BY id", account_id)


async def get_enabled_groups(account_id):
    async with pool().acquire() as con:
        return await con.fetch("SELECT * FROM groups WHERE account_id=$1 AND is_enabled=TRUE", account_id)


async def remove_group(group_id):
    async with pool().acquire() as con:
        await con.execute("DELETE FROM groups WHERE id=$1", group_id)


async def clear_groups(account_id):
    async with pool().acquire() as con:
        await con.execute("DELETE FROM groups WHERE account_id=$1", account_id)


async def count_groups(account_id):
    async with pool().acquire() as con:
        return await con.fetchval("SELECT COUNT(*) FROM groups WHERE account_id=$1", account_id)


async def set_group_enabled(group_id, enabled):
    async with pool().acquire() as con:
        await con.execute("UPDATE groups SET is_enabled=$1 WHERE id=$2", enabled, group_id)


async def enable_all_groups(account_id, enabled=True):
    async with pool().acquire() as con:
        await con.execute("UPDATE groups SET is_enabled=$1 WHERE account_id=$2", enabled, account_id)


# ═══ AUTOSEND ═══════════════════════════════════════════════════════
async def get_autosend(account_id):
    async with pool().acquire() as con:
        row = await con.fetchrow("SELECT * FROM autosend WHERE account_id=$1", account_id)
        if not row:
            await con.execute("INSERT INTO autosend (account_id) VALUES ($1) ON CONFLICT DO NOTHING", account_id)
            row = await con.fetchrow("SELECT * FROM autosend WHERE account_id=$1", account_id)
        return row


async def update_autosend(account_id, **fields):
    if not fields:
        return
    cols = ", ".join(f"{k}=${i+2}" for i, k in enumerate(fields))
    async with pool().acquire() as con:
        await con.execute(f"UPDATE autosend SET {cols} WHERE account_id=$1",
                          account_id, *fields.values())


async def set_running(account_id, running, next_send_at=None):
    async with pool().acquire() as con:
        await con.execute(
            "UPDATE autosend SET is_running=$1, next_send_at=$2 WHERE account_id=$3",
            running, next_send_at, account_id)


async def inc_cycle(account_id):
    async with pool().acquire() as con:
        await con.execute("UPDATE autosend SET cycles=cycles+1 WHERE account_id=$1", account_id)


# ═══ DM REPLY ═══════════════════════════════════════════════════════
async def get_dm_reply(account_id):
    async with pool().acquire() as con:
        row = await con.fetchrow("SELECT * FROM dm_reply WHERE account_id=$1", account_id)
        if not row:
            await con.execute("INSERT INTO dm_reply (account_id) VALUES ($1) ON CONFLICT DO NOTHING", account_id)
            row = await con.fetchrow("SELECT * FROM dm_reply WHERE account_id=$1", account_id)
        return row


async def update_dm_reply(account_id, **fields):
    if not fields:
        return
    cols = ", ".join(f"{k}=${i+2}" for i, k in enumerate(fields))
    async with pool().acquire() as con:
        await con.execute(f"UPDATE dm_reply SET {cols}, updated_at=NOW() WHERE account_id=$1",
                          account_id, *fields.values())


# ═══ GROUP REPLY ════════════════════════════════════════════════════
async def get_group_reply(account_id):
    async with pool().acquire() as con:
        row = await con.fetchrow("SELECT * FROM group_reply WHERE account_id=$1", account_id)
        if not row:
            await con.execute("INSERT INTO group_reply (account_id) VALUES ($1) ON CONFLICT DO NOTHING", account_id)
            row = await con.fetchrow("SELECT * FROM group_reply WHERE account_id=$1", account_id)
        return row


async def update_group_reply(account_id, **fields):
    if not fields:
        return
    cols = ", ".join(f"{k}=${i+2}" for i, k in enumerate(fields))
    async with pool().acquire() as con:
        await con.execute(f"UPDATE group_reply SET {cols}, updated_at=NOW() WHERE account_id=$1",
                          account_id, *fields.values())


# ═══ STATS ══════════════════════════════════════════════════════════
async def log_send(account_id, chat_id, status, error=""):
    async with pool().acquire() as con:
        await con.execute(
            "INSERT INTO send_log (account_id, chat_id, status, error) VALUES ($1,$2,$3,$4)",
            account_id, chat_id, status, error)


async def get_stats(account_id):
    async with pool().acquire() as con:
        total = await con.fetchval("SELECT COUNT(*) FROM send_log WHERE account_id=$1", account_id)
        sent = await con.fetchval("SELECT COUNT(*) FROM send_log WHERE account_id=$1 AND status='sent'", account_id)
        failed = await con.fetchval("SELECT COUNT(*) FROM send_log WHERE account_id=$1 AND status='failed'", account_id)
        today = await con.fetchval(
            "SELECT COUNT(*) FROM send_log WHERE account_id=$1 AND status='sent' AND sent_at::date=CURRENT_DATE", account_id)
    return {"total": total, "sent": sent, "failed": failed, "today": today}


async def get_global_stats():
    async with pool().acquire() as con:
        users = await con.fetchval("SELECT COUNT(*) FROM users")
        accounts = await con.fetchval("SELECT COUNT(*) FROM accounts")
        active = await con.fetchval("SELECT COUNT(*) FROM autosend WHERE is_running=TRUE")
        groups = await con.fetchval("SELECT COUNT(*) FROM groups")
        sent_total = await con.fetchval("SELECT COUNT(*) FROM send_log WHERE status='sent'")
        premium = await con.fetchval("SELECT COUNT(*) FROM users WHERE is_premium=TRUE")
    return {"users": users, "accounts": accounts, "active": active,
            "groups": groups, "sent_total": sent_total, "premium": premium}


# ═══ CHANNELS (majburiy obuna) ══════════════════════════════════════
async def add_channel(channel_id, title, invite_url):
    async with pool().acquire() as con:
        await con.execute(
            "INSERT INTO channels (channel_id, title, invite_url) VALUES ($1,$2,$3)",
            channel_id, title, invite_url)


async def get_channels():
    async with pool().acquire() as con:
        return await con.fetch("SELECT * FROM channels ORDER BY id")


async def remove_channel(ch_id):
    async with pool().acquire() as con:
        await con.execute("DELETE FROM channels WHERE id=$1", ch_id)


# ═══ TICKETS (murojat) ══════════════════════════════════════════════
async def create_ticket(user_id, username, message):
    async with pool().acquire() as con:
        return await con.fetchrow(
            "INSERT INTO tickets (user_id, username, message) VALUES ($1,$2,$3) RETURNING *",
            user_id, username, message)


async def close_ticket(ticket_id):
    async with pool().acquire() as con:
        await con.execute("UPDATE tickets SET status='closed' WHERE id=$1", ticket_id)


# ═══ SETTINGS ═══════════════════════════════════════════════════════
async def get_setting(key, default=""):
    async with pool().acquire() as con:
        val = await con.fetchval("SELECT value FROM settings WHERE key=$1", key)
        return val if val is not None else default


async def set_setting(key, value):
    async with pool().acquire() as con:
        await con.execute(
            "INSERT INTO settings (key, value) VALUES ($1,$2) ON CONFLICT (key) DO UPDATE SET value=$2",
            key, value)
