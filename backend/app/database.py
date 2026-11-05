import os
import sqlite3
import pymysql
import pymysql.cursors
from typing import Optional, Dict, Any, List
from pathlib import Path
from contextlib import contextmanager
from backend.app.config import settings, BASE_DIR

SQLITE_PATH = BASE_DIR / "techiepark_dev.db"
DB_MODE = "unknown"  # Will be "mysql" or "sqlite"

def test_mysql_connection() -> bool:
    """Test if MySQL is accessible with the configured settings."""
    if not settings.DB_PASSWORD:
        return False
    try:
        conn = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            charset="utf8mb4",
            connect_timeout=2
        )
        conn.close()
        return True
    except Exception:
        return False

def get_mysql_connection(include_db: bool = True):
    return pymysql.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME if include_db else None,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=2,
        autocommit=True
    )

def get_sqlite_connection():
    conn = sqlite3.connect(str(SQLITE_PATH), timeout=5)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> bool:
    """Initialize database tables in MySQL or fallback to local SQLite."""
    global DB_MODE
    if test_mysql_connection():
        try:
            # 1. Create DB if not exists
            server_conn = get_mysql_connection(include_db=False)
            with server_conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{settings.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            server_conn.close()

            # 2. Create tables
            conn = get_mysql_connection(include_db=True)
            with conn.cursor() as cursor:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(120) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NULL,
                    auth_provider VARCHAR(50) DEFAULT 'local',
                    google_id VARCHAR(255) NULL UNIQUE,
                    avatar_url VARCHAR(500) NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL UNIQUE,
                    bio TEXT NULL,
                    linkedin_url VARCHAR(500) NULL,
                    leetcode_url VARCHAR(500) NULL,
                    github_url VARCHAR(500) NULL,
                    cv_filename VARCHAR(255) NULL,
                    is_completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
            conn.close()
            DB_MODE = "mysql"
            print("✓ [Database] Connected to MySQL successfully! Database & tables verified.")
            return True
        except Exception as e:
            print(f"Warning: MySQL initialization encountered error: {e}")

    # Fallback to SQLite so the user can test the app right away
    DB_MODE = "sqlite"
    print("ℹ [Database] MySQL not reachable yet (Please set DB_PASSWORD in .env).")
    print(f"✓ [Database] Using seamless local fallback ({SQLITE_PATH.name}) so you can test registration & login immediately!")
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NULL,
        auth_provider TEXT DEFAULT 'local',
        google_id TEXT UNIQUE,
        avatar_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        bio TEXT,
        linkedin_url TEXT,
        leetcode_url TEXT,
        github_url TEXT,
        cv_filename TEXT,
        is_completed BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()
    return True

# --- User Data Access Helpers ---

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    global DB_MODE
    email_clean = email.strip().lower()
    if DB_MODE == "mysql":
        conn = get_mysql_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s LIMIT 1", (email_clean,))
            row = cursor.fetchone()
        conn.close()
        return row
    else:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? LIMIT 1", (email_clean,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    global DB_MODE
    if DB_MODE == "mysql":
        conn = get_mysql_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, full_name, email, auth_provider, avatar_url, created_at FROM users WHERE id = %s LIMIT 1", (user_id,))
            row = cursor.fetchone()
        conn.close()
        return row
    else:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, email, auth_provider, avatar_url, created_at FROM users WHERE id = ? LIMIT 1", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

def create_local_user(full_name: str, email: str, password_hash: str) -> int:
    global DB_MODE
    email_clean = email.strip().lower()
    name_clean = full_name.strip()
    if DB_MODE == "mysql":
        conn = get_mysql_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (full_name, email, password_hash, auth_provider) VALUES (%s, %s, %s, 'local')",
                (name_clean, email_clean, password_hash)
            )
            user_id = cursor.lastrowid
            cursor.execute("INSERT INTO profiles (user_id, is_completed) VALUES (%s, FALSE)", (user_id,))
        conn.close()
        return user_id
    else:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (full_name, email, password_hash, auth_provider) VALUES (?, ?, ?, 'local')",
            (name_clean, email_clean, password_hash)
        )
        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO profiles (user_id, is_completed) VALUES (?, 0)", (user_id,))
        conn.commit()
        conn.close()
        return user_id

def create_or_get_google_user(email: str, full_name: str, google_id: str, avatar_url: Optional[str] = None) -> Dict[str, Any]:
    global DB_MODE
    email_clean = email.strip().lower()
    if DB_MODE == "mysql":
        conn = get_mysql_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s OR google_id = %s LIMIT 1", (email_clean, google_id))
            user = cursor.fetchone()
            if not user:
                cursor.execute(
                    "INSERT INTO users (full_name, email, auth_provider, google_id, avatar_url) VALUES (%s, %s, 'google', %s, %s)",
                    (full_name, email_clean, google_id, avatar_url)
                )
                user_id = cursor.lastrowid
                cursor.execute("INSERT INTO profiles (user_id, is_completed) VALUES (%s, FALSE)", (user_id,))
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                user = cursor.fetchone()
        conn.close()
        return user
    else:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? OR google_id = ? LIMIT 1", (email_clean, google_id))
        row = cursor.fetchone()
        if not row:
            cursor.execute(
                "INSERT INTO users (full_name, email, auth_provider, google_id, avatar_url) VALUES (?, ?, 'google', ?, ?)",
                (full_name, email_clean, google_id, avatar_url)
            )
            user_id = cursor.lastrowid
            cursor.execute("INSERT INTO profiles (user_id, is_completed) VALUES (?, 0)", (user_id,))
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
        conn.close()
        return dict(row)

def check_profile_completed(user_id: int) -> bool:
    global DB_MODE
    try:
        if DB_MODE == "mysql":
            conn = get_mysql_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT is_completed FROM profiles WHERE user_id = %s", (user_id,))
                res = cursor.fetchone()
            conn.close()
            return bool(res.get("is_completed")) if res else False
        else:
            conn = get_sqlite_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT is_completed FROM profiles WHERE user_id = ?", (user_id,))
            res = cursor.fetchone()
            conn.close()
            return bool(res["is_completed"]) if res else False
    except Exception:
        return False
