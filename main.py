# -*- coding: utf-8 -*-
import uvicorn
import random
import os
import sys
import multiprocessing
import hashlib
import hmac
import base64
import json
import time
import threading
import webbrowser
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# ---- Аватарки авторов ----
try:
    from avatars import AVATAR_TAKAYO, AVATAR_SANDGAR, AVATAR_LAZARET
except ImportError:
    AVATAR_TAKAYO = "👤"
    AVATAR_SANDGAR = "👤"
    AVATAR_LAZARET = "👤"

# ============ НАСТРОЙКИ ============
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24 * 7
PORT = int(os.environ.get("PORT", 8000))
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Определяем какой драйвер БД использовать
USE_POSTGRES = DATABASE_URL.startswith("postgres")

if USE_POSTGRES:
    import psycopg2
    import psycopg2.extras
else:
    import sqlite3

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SQLITE_PATH = os.path.join(BASE_DIR, "pbk.db")

# ============ УНИВЕРСАЛЬНАЯ РАБОТА С БД ============
def get_db():
    """Возвращает соединение с БД (PostgreSQL или SQLite)"""
    if USE_POSTGRES:
        return psycopg2.connect(DATABASE_URL)
    return sqlite3.connect(SQLITE_PATH)

def ph(query: str) -> str:
    """Заменяет ? на %s если используется PostgreSQL"""
    if USE_POSTGRES:
        return query.replace("?", "%s")
    return query

def fetchone(cursor):
    """Возвращает одну строку как словарь/кортеж"""
    return cursor.fetchone()

# ============ ХЭШ ПАРОЛЕЙ ============
def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
    return base64.b64encode(salt + dk).decode()

def verify_password(password: str, hashed: str) -> bool:
    try:
        raw = base64.b64decode(hashed.encode())
        salt, dk = raw[:16], raw[16:]
        new_dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
        return hmac.compare_digest(dk, new_dk)
    except Exception:
        return False

# ============ JWT ============
def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def _b64d(s: str) -> bytes:
    pad = '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)

def create_access_token(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = payload.copy()
    payload["exp"] = int(time.time()) + ACCESS_TOKEN_EXPIRE_SECONDS
    h = _b64(json.dumps(header, separators=(',', ':')).encode())
    p = _b64(json.dumps(payload, separators=(',', ':')).encode())
    signing_input = f"{h}.{p}".encode()
    sig = hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    return f"{h}.{p}.{_b64(sig)}"

def decode_access_token(token: str):
    try:
        h, p, s = token.split('.')
        signing_input = f"{h}.{p}".encode()
        expected = hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64d(s)):
            return None
        payload = json.loads(_b64d(p))
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None

# ============ ИНИЦИАЛИЗАЦИЯ БД ============
def init_db():
    conn = get_db()
    c = conn.cursor()

    if USE_POSTGRES:
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            uid INTEGER UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            device_hash TEXT UNIQUE,
            avatar TEXT DEFAULT '👤',
            balance REAL DEFAULT 1000.0,
            hamster_coins INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            type TEXT,
            amount REAL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            username TEXT,
            text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
    else:
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid INTEGER UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            device_hash TEXT UNIQUE,
            avatar TEXT DEFAULT '👤',
            balance REAL DEFAULT 1000.0,
            hamster_coins INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            amount REAL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

    conn.commit()
    conn.close()

# ============ АВТОРИЗАЦИЯ ============
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учётные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if not payload:
        raise exc
    username = payload.get("sub")
    if not username:
        raise exc

    conn = get_db()
    c = conn.cursor()
    c.execute(ph("SELECT id, uid, username, balance, hamster_coins, avatar FROM users WHERE username=?"), (username,))
    user = c.fetchone()
    conn.close()
    if not user:
        raise exc
    return {"id": user[0], "uid": user[1], "username": user[2],
            "balance": user[3], "hamster_coins": user[4], "avatar": user[5]}

def generate_uid():
    conn = get_db()
    c = conn.cursor()
    for _ in range(10000):
        uid = random.randint(1000, 9999)
        c.execute(ph("SELECT id FROM users WHERE uid=?"), (uid,))
        if not c.fetchone():
            conn.close()
            return uid
    conn.close()
    raise HTTPException(500, "Свободных UID не осталось")

# ============ МОДЕЛИ ============
class RegisterData(BaseModel):
    username: str
    password: str
    device_hash: str = ""

class AmountData(BaseModel):
    amount: float

class TransferData(BaseModel):
    to_uid: int
    amount: float

class SupportData(BaseModel):
    message: str

class AvatarData(BaseModel):
    avatar: str

class UsernameData(BaseModel):
    username: str

# ============ APP ============
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="ПБК Wallet", lifespan=lifespan)

# ============ WEBSOCKET ============
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                dead.append(connection)
        for d in dead:
            self.disconnect(d)

manager = ConnectionManager()

# ============ API ============
@app.post("/api/register")
def register(data: RegisterData):
    if len(data.username) < 3:
        raise HTTPException(400, "Ник слишком короткий (мин. 3 символа)")
    if len(data.password) < 3 or len(data.password) > 20:
        raise HTTPException(400, "Пароль должен быть от 3 до 20 символов")

    conn = get_db()
    c = conn.cursor()
    c.execute(ph("SELECT id FROM users WHERE username=?"), (data.username,))
    if c.fetchone():
        conn.close()
        raise HTTPException(400, "Такой ник уже занят")

    if data.device_hash:
        c.execute(ph("SELECT uid FROM users WHERE device_hash=?"), (data.device_hash,))
        existing = c.fetchone()
        if existing:
            conn.close()
            raise HTTPException(400, f"Это устройство уже привязано к аккаунту #{existing[0]}")

    uid = generate_uid()
    hashed = hash_password(data.password)

    if USE_POSTGRES:
        c.execute(
            "INSERT INTO users (uid, username, hashed_password, device_hash, avatar) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (uid, data.username, hashed, data.device_hash or None, "👤")
        )
        user_id = c.fetchone()[0]
    else:
        c.execute(
            "INSERT INTO users (uid, username, hashed_password, device_hash, avatar) VALUES (?, ?, ?, ?, ?)",
            (uid, data.username, hashed, data.device_hash or None, "👤")
        )
        user_id = c.lastrowid

    c.execute(ph("INSERT INTO transactions (user_id, type, amount, comment) VALUES (?, ?, ?, ?)"),
              (user_id, "bonus", 1000.0, "Приветственный бонус от ПБК Wallet"))
    conn.commit()
    conn.close()

    token = create_access_token({"sub": data.username})
    return {"message": "Добро пожаловать!",
            "uid": uid, "username": data.username, "avatar": "👤",
            "access_token": token, "token_type": "bearer"}

@app.post("/api/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db()
    c = conn.cursor()
    c.execute(ph("SELECT id, uid, username, hashed_password, avatar FROM users WHERE username=?"),
              (form_data.username,))
    user = c.fetchone()
    conn.close()
    if not user or not verify_password(form_data.password, user[3]):
        raise HTTPException(401, "Неверный логин или пароль")
    token = create_access_token({"sub": user[2]})
    return {"access_token": token, "token_type": "bearer",
            "uid": user[1], "username": user[2], "avatar": user[4]}

@app.get("/api/me")
def me(current=Depends(get_current_user)):
    return {"uid": current["uid"], "username": current["username"],
            "balance": round(current["balance"], 2),
            "hamster_coins": current["hamster_coins"], "avatar": current["avatar"]}

@app.post("/api/deposit")
def deposit(data: AmountData, current=Depends(get_current_user)):
    if data.amount <= 0:
        raise HTTPException(400, "Сумма должна быть положительной")
    fee = round(data.amount * 0.15, 2)
    net = round(data.amount - fee, 2)
    conn = get_db()
    c = conn.cursor()
    c.execute(ph("UPDATE users SET balance = balance + ? WHERE id=?"), (net, current["id"]))
    c.execute(ph("INSERT INTO transactions (user_id, type, amount, comment) VALUES (?, ?, ?, ?)"),
              (current["id"], "deposit", data.amount,
               f"Пополнение {data.amount}₽, комиссия {fee}₽"))
    conn.commit()
    c.execute(ph("SELECT balance FROM users WHERE id=?"), (current["id"],))
    new_balance = c.fetchone()[0]
    conn.close()
    return {"message": f"Принято {data.amount}₽. Комиссия {fee}₽.",
            "balance": new_balance}

@app.post("/api/withdraw")
def withdraw(data: AmountData, current=Depends(get_current_user)):
    reasons = [
        "Извините, операция временно недоступна. Попробуйте через 3–5 рабочих лет.",
        "Отдел снятия наличных ушёл на обед. В 2019 году.",
        "Ваша заявка рассматривается. Рассмотрение застряло.",
        "ПБК Wallet временно не выдаёт деньги. И постоянно тоже.",
        "Ошибка 402: Денег нет, но вы держитесь.",
        "Служба поддержки сказала: «Не сегодня».",
    ]
    reason = random.choice(reasons)
    conn = get_db()
    c = conn.cursor()
    c.execute(ph("INSERT INTO transactions (user_id, type, amount, comment) VALUES (?, ?, ?, ?)"),
              (current["id"], "withdraw_denied", data.amount, reason))
    conn.commit()
    conn.close()
    return {"message": reason, "balance": current["balance"]}

@app.post("/api/transfer")
def transfer(data: TransferData, current=Depends(get_current_user)):
    if data.amount <= 0:
        raise HTTPException(400, "Сумма должна быть положительной")
    if data.amount > current["balance"]:
        raise HTTPException(400, "Недостаточно средств")
    conn = get_db()
    c = conn.cursor()
    c.execute(ph("SELECT id, username FROM users WHERE uid=?"), (data.to_uid,))
    recipient = c.fetchone()
    if not recipient:
        conn.close()
        raise HTTPException(404, f"Пользователь с UID #{data.to_uid} не найден")
    if recipient[0] == current["id"]:
        conn.close()
        raise HTTPException(400, "Нельзя переводить самому себе")
    c.execute(ph("UPDATE users SET balance = balance - ? WHERE id=?"), (data.amount, current["id"]))
    c.execute(ph("UPDATE users SET balance = balance + ? WHERE id=?"), (data.amount, recipient[0]))
    c.execute(ph("INSERT INTO transactions (user_id, type, amount, comment) VALUES (?, ?, ?, ?)"),
              (current["id"], "transfer_out", data.amount,
               f"Перевод пользователю #{data.to_uid} ({recipient[1]})"))
    c.execute(ph("INSERT INTO transactions (user_id, type, amount, comment) VALUES (?, ?, ?, ?)"),
              (recipient[0], "transfer_in", data.amount,
               f"Перевод от #{current['uid']} ({current['username']})"))
    conn.commit()
    c.execute(ph("SELECT balance FROM users WHERE id=?"), (current["id"],))
    new_balance = c.fetchone()[0]
    conn.close()
    return {"message": f"Переведено {data.amount}₽ пользователю #{data.to_uid}",
            "balance": new_balance}

@app.get("/api/transactions")
def transactions(current=Depends(get_current_user)):
    conn = get_db()
    c = conn.cursor()
    c.execute(ph("SELECT type, amount, comment, created_at FROM transactions "
                 "WHERE user_id=? ORDER BY created_at DESC LIMIT 100"), (current["id"],))
    rows = c.fetchall()
    conn.close()
    return [{"type": r[0], "amount": r[1], "comment": r[2], "created_at": str(r[3])} for r in rows]

@app.post("/api/support")
def support(data: SupportData, current=Depends(get_current_user)):
    msg = data.message.lower()
    responses = {
        "баланс": f"Ваш баланс: {current['balance']:.2f}₽.",
        "снять": "Снятие временно недоступно. Попробуйте позже.",
        "перевод": "Переводы работают. Иногда.",
        "привет": f"Привет, {current['username']}! Чем могу помочь?",
        "пароль": "Пароль? Не подскажем.",
    }
    for key, response in responses.items():
        if key in msg:
            return {"reply": response}
    defaults = [
        "Мы всё видим. Мы всё знаем. Мы не вернём.",
        "Обратитесь в поддержку через 3-5 рабочих лет.",
        "Ваш вопрос очень важен для нас.",
        "Технические работы. Вечные.",
        "Спасибо за обращение! Ваш запрос #1337 обрабатывается.",
    ]
    return {"reply": random.choice(defaults)}

@app.post("/api/avatar")
def set_avatar(data: AvatarData, current=Depends(get_current_user)):
    conn = get_db()
    c = conn.cursor()
    c.execute(ph("UPDATE users SET avatar=? WHERE id=?"), (data.avatar, current["id"]))
    conn.commit()
    conn.close()
    return {"message": "Аватар обновлён", "avatar": data.avatar}

@app.post("/api/username")
def change_username(data: UsernameData, current=Depends(get_current_user)):
    new_name = data.username.strip()
    if len(new_name) < 3 or len(new_name) > 20:
        raise HTTPException(400, "Ник должен быть от 3 до 20 символов")
    conn = get_db()
    c = conn.cursor()
    c.execute(ph("SELECT id FROM users WHERE username=? AND id != ?"), (new_name, current["id"]))
    if c.fetchone():
        conn.close()
        raise HTTPException(400, "Такой ник уже занят")
    c.execute(ph("UPDATE users SET username=? WHERE id=?"), (new_name, current["id"]))
    conn.commit()
    conn.close()
    token = create_access_token({"sub": new_name})
    return {"message": "Ник изменён", "username": new_name, "access_token": token, "token_type": "bearer"}

@app.get("/api/messages")
def get_messages(current=Depends(get_current_user)):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT user_id, username, text, created_at FROM messages "
              "ORDER BY created_at DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    return [{"user_id": r[0], "username": r[1], "text": r[2], "created_at": str(r[3])}
            for r in reversed(rows)]

@app.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket, token: str = ""):
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=1008)
        return
    username = payload.get("sub")

    conn = get_db()
    c = conn.cursor()
    c.execute(ph("SELECT id, username FROM users WHERE username=?"), (username,))
    user = c.fetchone()
    if not user:
        conn.close()
        await websocket.close(code=1008)
        return
    c.execute("SELECT username, text, created_at FROM messages "
              "ORDER BY created_at DESC LIMIT 30")
    history = c.fetchall()
    conn.close()

    await manager.connect(websocket)
    for msg in history:
        await websocket.send_text(f"[{msg[2]}] {msg[0]}: {msg[1]}")

    try:
        while True:
            data = await websocket.receive_text()
            conn = get_db()
            c = conn.cursor()
            c.execute(ph("INSERT INTO messages (user_id, username, text) VALUES (?, ?, ?)"),
                      (user[0], user[1], data))
            conn.commit()
            conn.close()
            await manager.broadcast(
                f"[{datetime.now().strftime('%H:%M')}] {user[1]}: {data}"
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ============ ЗАПУСК ============
def open_browser():
    if os.environ.get("RENDER"):
        return
    time.sleep(1.5)
    try:
        webbrowser.open(f"http://127.0.0.1:{PORT}")
    except Exception:
        pass

# ============================================================
# ==================== ФРОНТЕНД ==============================
# ============================================================

INDEX_HTML = r"""<!DOCTYPE html>
<html lang="ru" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ПБК Wallet</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🏦</text></svg>">
<style>
:root {
  --bg: #f5faff; --bg-alt: #ffffff; --card: #ffffff;
  --card-glass: rgba(255,255,255,0.65);
  --sidebar-glass: rgba(255,255,255,0.55);
  --topbar-glass: rgba(255,255,255,0.6);
  --primary: #2196f3; --primary-dark: #1565c0; --primary-light: #bbdefb; --primary-soft: #e3f2fd;
  --text: #0d2a4a; --text-muted: #5a7996; --border: #d6e6f7;
  --shadow: 0 8px 24px rgba(33,150,243,0.10);
  --danger: #e53935; --success: #2e7d32;
}
[data-theme="dark"] {
  --bg: #0b1c2c; --bg-alt: #102a43; --card: #143654;
  --card-glass: rgba(20,54,84,0.65);
  --sidebar-glass: rgba(16,42,67,0.6);
  --topbar-glass: rgba(16,42,67,0.65);
  --primary: #64b5f6; --primary-dark: #2196f3; --primary-light: #1e4d75; --primary-soft: #17385a;
  --text: #eaf3fb; --text-muted: #9fb8d0; --border: #1e4d75;
  --shadow: 0 8px 24px rgba(0,0,0,0.35);
  --danger: #ef5350; --success: #66bb6a;
}
[data-theme="graphite"] {
  --bg: #1a1a1a; --bg-alt: #242424; --card: #2a2a2a;
  --card-glass: rgba(42,42,42,0.7);
  --sidebar-glass: rgba(36,36,36,0.75);
  --topbar-glass: rgba(36,36,36,0.75);
  --primary: #90a4ae; --primary-dark: #607d8b; --primary-light: #37474f; --primary-soft: #37474f;
  --text: #eceff1; --text-muted: #b0bec5; --border: #37474f;
  --shadow: 0 8px 24px rgba(0,0,0,0.5);
  --danger: #ef5350; --success: #66bb6a;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "Segoe UI", system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); transition: background .25s, color .25s; min-height: 100vh; }
button { font-family: inherit; cursor: pointer; }
input, button { font-size: 15px; }
.hidden { display: none !important; }

body.glass .sidebar { background: var(--sidebar-glass); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); }
body.glass .topbar { background: var(--topbar-glass); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); }
body.glass .card { background: var(--card-glass); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); }
body.glass .auth-card { background: var(--card-glass); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); }

.auth-wrap { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; background: linear-gradient(135deg, var(--primary-soft) 0%, var(--bg) 60%); }
.auth-card { background: var(--card); border-radius: 24px; padding: 40px 32px; width: 100%; max-width: 420px; box-shadow: var(--shadow); border: 1px solid var(--border); position: relative; }
.auth-logo { display: flex; align-items: center; justify-content: center; gap: 10px; font-weight: 800; font-size: 28px; color: var(--primary-dark); margin-bottom: 8px; }
.auth-logo svg { color: var(--primary); }
.auth-disclaimer { text-align: center; color: var(--text-muted); font-size: 11px; margin-bottom: 20px; line-height: 1.4; }
.auth-tabs { display: flex; gap: 8px; margin-bottom: 20px; }
.tab-btn { flex: 1; padding: 10px; border: none; border-radius: 12px; background: var(--primary-soft); color: var(--primary-dark); font-weight: 600; transition: all .2s; }
.tab-btn.active { background: var(--primary); color: #fff; }
.auth-form { display: flex; flex-direction: column; gap: 12px; }
.auth-form input { padding: 14px 16px; border-radius: 12px; border: 1px solid var(--border); background: var(--bg-alt); color: var(--text); transition: all .2s; }
.auth-form input:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-soft); }
.auth-hint { color: var(--text-muted); font-size: 12px; text-align: center; }
.auth-theme { position: absolute; top: 16px; right: 16px; }
.theme-toggle { background: var(--primary-soft); color: var(--primary-dark); border: none; border-radius: 50%; width: 40px; height: 40px; font-size: 18px; transition: background .2s; }
.theme-toggle:hover { background: var(--primary-light); }

.btn { border: none; padding: 12px 20px; border-radius: 12px; font-weight: 600; background: var(--primary); color: #fff; box-shadow: 0 4px 12px rgba(33,150,243,.25); transition: all .2s; }
.btn:hover { background: var(--primary-dark); transform: translateY(-1px); }
.btn-ghost { background: transparent; color: var(--primary-dark); box-shadow: none; border: 1px solid var(--border); }
.btn-ghost:hover { background: var(--primary-soft); }
.btn-danger { background: var(--danger); }

.app-body { display: flex; min-height: 100vh; }
.sidebar { width: 240px; background: var(--card); border-right: 1px solid var(--border); padding: 20px 14px; display: flex; flex-direction: column; gap: 6px; position: sticky; top: 0; height: 100vh; transition: background .25s, backdrop-filter .25s; }
.sidebar-logo { display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 22px; color: var(--primary-dark); padding: 8px 10px 20px; }
.sidebar-logo svg { color: var(--primary); }
.nav-item { display: flex; align-items: center; gap: 12px; padding: 12px 14px; border-radius: 12px; color: var(--text); text-decoration: none; font-weight: 500; transition: all .15s; cursor: pointer; }
.nav-item:hover { background: var(--primary-soft); }
.nav-item.active { background: var(--primary); color: #fff; box-shadow: 0 4px 12px rgba(33,150,243,.3); }
.nav-icon { font-size: 18px; }
.sidebar-bottom { margin-top: auto; padding-top: 12px; }

.main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.topbar { padding: 16px 28px; border-bottom: 1px solid var(--border); background: var(--card); display: flex; justify-content: flex-end; align-items: center; gap: 14px; transition: background .25s, backdrop-filter .25s; }
.topbar-user { display: flex; align-items: center; gap: 10px; padding: 8px 14px; background: var(--primary-soft); border-radius: 999px; font-weight: 600; color: var(--primary-dark); }
.topbar-uid { opacity: .7; font-weight: 500; font-size: 13px; }
.content { padding: 28px; max-width: 1000px; width: 100%; }
.page { display: none; }
.page.active { display: block; animation: fade .25s ease; }
@keyframes fade { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }

.card { background: var(--card); border-radius: 20px; padding: 24px; box-shadow: var(--shadow); border: 1px solid var(--border); margin-bottom: 20px; transition: background .25s, backdrop-filter .25s; }
.card h3 { margin-bottom: 12px; color: var(--primary-dark); }
.muted { color: var(--text-muted); font-size: 14px; margin-bottom: 12px; }
input[type="number"], input[type="text"], input[type="password"], select { width: 100%; padding: 12px 14px; border-radius: 12px; border: 1px solid var(--border); background: var(--bg-alt); color: var(--text); margin-bottom: 10px; transition: all .2s; }
input:focus, select:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-soft); }

.balance-card { background: linear-gradient(135deg, var(--primary), var(--primary-dark)); color: #fff; border-radius: 24px; padding: 32px; box-shadow: 0 12px 32px rgba(33,150,243,.35); margin-bottom: 24px; }
.balance-label { opacity: .85; font-size: 13px; letter-spacing: 1.5px; }
.balance-amount { font-size: 44px; font-weight: 800; margin: 6px 0 8px; }
.balance-uid { opacity: .85; font-size: 14px; }

.actions-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }
.tx-list { list-style: none; }
.tx-list li { padding: 14px 0; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; gap: 12px; }
.tx-list li:last-child { border-bottom: none; }
.tx-comment { color: var(--text-muted); font-size: 13px; margin-top: 4px; }
.tx-amount { font-weight: 700; white-space: nowrap; }
.tx-amount.plus { color: var(--success); }
.tx-amount.minus { color: var(--danger); }

.chat-card { display: flex; flex-direction: column; height: calc(100vh - 180px); min-height: 400px; }
.chat-messages { flex: 1; overflow-y: auto; padding: 14px; background: var(--bg-alt); border-radius: 14px; border: 1px solid var(--border); margin-bottom: 12px; font-size: 14px; line-height: 1.6; }
.chat-messages > div { padding: 4px 0; word-wrap: break-word; }
.chat-input-row { display: flex; gap: 10px; }
.chat-input-row input { margin-bottom: 0; flex: 1; }

.team-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-top: 12px; }
.team-card { text-align: center; padding: 20px 16px; border-radius: 16px; background: var(--primary-soft); }
.team-avatar { width: 120px; height: 120px; border-radius: 50%; object-fit: cover; margin: 0 auto 12px; display: block; border: 3px solid var(--primary); background: var(--card); }
.team-name { font-weight: 700; color: var(--primary-dark); font-size: 17px; }
.team-role { color: var(--text-muted); font-size: 13px; margin-top: 4px; }

.profile-row { display: flex; align-items: center; gap: 20px; margin-bottom: 24px; }
.profile-avatar-big { font-size: 64px; width: 96px; height: 96px; display: flex; align-items: center; justify-content: center; background: var(--primary-soft); border-radius: 50%; overflow: hidden; }
.profile-avatar-big img { width: 100%; height: 100%; object-fit: cover; }
.profile-username { font-size: 24px; font-weight: 700; color: var(--primary-dark); }

.avatar-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; margin: 12px 0 20px; }
.avatar-option { font-size: 28px; padding: 10px; border-radius: 12px; border: 2px solid transparent; background: var(--primary-soft); transition: all .15s; }
.avatar-option:hover { transform: scale(1.08); }
.avatar-option.selected { border-color: var(--primary); background: var(--primary-light); }

.settings-row { display: flex; justify-content: space-between; align-items: center; padding: 14px 0; border-bottom: 1px solid var(--border); }
.settings-row:last-child { border-bottom: none; }
.settings-label { font-weight: 600; }
.settings-desc { color: var(--text-muted); font-size: 13px; margin-top: 2px; }
.settings-control select { width: auto; margin-bottom: 0; min-width: 160px; }

.switch { position: relative; display: inline-block; width: 52px; height: 28px; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background: var(--border); transition: .3s; border-radius: 28px; }
.slider:before { position: absolute; content: ""; height: 22px; width: 22px; left: 3px; bottom: 3px; background: white; transition: .3s; border-radius: 50%; }
input:checked + .slider { background: var(--primary); }
input:checked + .slider:before { transform: translateX(24px); }

#toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%) translateY(80px); background: var(--primary-dark); color: #fff; padding: 14px 22px; border-radius: 12px; box-shadow: var(--shadow); max-width: 90%; text-align: center; font-weight: 500; transition: all .3s; z-index: 100; opacity: 0; }
#toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }
#toast.error { background: var(--danger); }
#toast.success { background: var(--success); }

.avatar-upload-row { display: flex; gap: 10px; align-items: center; margin: 12px 0; flex-wrap: wrap; }
.avatar-upload-row input[type="file"] { display: none; }
.avatar-upload-label { display: inline-block; padding: 10px 16px; border-radius: 12px; background: var(--primary-soft); color: var(--primary-dark); cursor: pointer; font-weight: 600; border: 1px solid var(--border); }
.avatar-upload-label:hover { background: var(--primary-light); }

@media (max-width: 720px) {
  .sidebar { width: 68px; padding: 14px 8px; }
  .sidebar-logo span, .nav-item span:not(.nav-icon) { display: none; }
  .nav-item { justify-content: center; padding: 12px; }
  .content { padding: 16px; }
  .balance-amount { font-size: 34px; }
  .avatar-grid { grid-template-columns: repeat(4, 1fr); }
}
</style>
</head>
<body>

<div class="auth-wrap" id="auth-screen">
  <div class="auth-card">
    <div class="auth-theme">
      <button class="theme-toggle" id="theme-toggle-auth" onclick="toggleTheme()">🌙</button>
    </div>
    <div class="auth-logo">
      <svg viewBox="0 0 24 24" width="34" height="34" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2 L12 6"/><path d="M9 22 L12 6 L15 22"/><path d="M10 15 L14 15"/><path d="M8.5 22 L15.5 22"/>
      </svg>
      <span>ПБК</span>
    </div>
    <div class="auth-disclaimer">Демонстрационный проект. Все операции виртуальные.</div>

    <div class="auth-tabs">
      <button class="tab-btn active" id="tab-login" onclick="switchTab('login')">Вход</button>
      <button class="tab-btn" id="tab-register" onclick="switchTab('register')">Регистрация</button>
    </div>

    <form class="auth-form" id="form-login" onsubmit="doLogin(event)">
      <input type="text" id="login-username" placeholder="Ник" required minlength="3" maxlength="20">
      <input type="password" id="login-password" placeholder="Пароль" required minlength="3" maxlength="20">
      <button class="btn" type="submit">Войти</button>
    </form>

    <form class="auth-form hidden" id="form-register" onsubmit="doRegister(event)">
      <input type="text" id="reg-username" placeholder="Ник (3–20 символов)" required minlength="3" maxlength="20">
      <input type="password" id="reg-password" placeholder="Пароль (3–20 символов)" required minlength="3" maxlength="20">
      <input type="password" id="reg-password2" placeholder="Подтвердите пароль" required minlength="3" maxlength="20">
      <button class="btn" type="submit">Создать аккаунт</button>
      <div class="auth-hint">Вам будет присвоен уникальный UID (4 цифры)</div>
    </form>
  </div>
</div>

<div class="app-body hidden" id="app-screen">
  <aside class="sidebar">
    <div class="sidebar-logo">
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2 L12 6"/><path d="M9 22 L12 6 L15 22"/><path d="M10 15 L14 15"/><path d="M8.5 22 L15.5 22"/>
      </svg>
      <span>ПБК</span>
    </div>
    <a class="nav-item active" data-page="wallet" onclick="switchPage('wallet')"><span class="nav-icon">🏦</span><span>Кошелёк</span></a>
    <a class="nav-item" data-page="transfer" onclick="switchPage('transfer')"><span class="nav-icon">💸</span><span>Перевести</span></a>
    <a class="nav-item" data-page="chat" onclick="switchPage('chat')"><span class="nav-icon">💬</span><span>Чат</span></a>
    <a class="nav-item" data-page="about" onclick="switchPage('about')"><span class="nav-icon">👥</span><span>О нас</span></a>
    <a class="nav-item" data-page="support" onclick="switchPage('support')"><span class="nav-icon">🆘</span><span>Поддержка</span></a>
    <a class="nav-item" data-page="settings" onclick="switchPage('settings')"><span class="nav-icon">⚙️</span><span>Настройки</span></a>
    <a class="nav-item" data-page="profile" onclick="switchPage('profile')"><span class="nav-icon">👤</span><span>Профиль</span></a>
    <div class="sidebar-bottom">
      <button class="theme-toggle" id="theme-toggle-app" onclick="toggleTheme()">🌙</button>
    </div>
  </aside>

  <main class="main">
    <div class="topbar">
      <div class="topbar-user">
        <span id="top-avatar">👤</span>
        <span id="top-username">—</span>
        <span class="topbar-uid" id="top-uid">#—</span>
      </div>
    </div>

    <div class="content">
      <section class="page active" id="page-wallet">
        <div class="balance-card">
          <div class="balance-label">ТЕКУЩИЙ БАЛАНС</div>
          <div class="balance-amount" id="balance">— ₽</div>
          <div class="balance-uid">UID: <span id="wallet-uid">#—</span></div>
        </div>
        <div class="actions-grid">
          <div class="card">
            <h3>Пополнить</h3>
            <div class="muted">Комиссия 15%.</div>
            <input type="number" id="deposit-amount" placeholder="Сумма, ₽" min="1">
            <button class="btn" onclick="doDeposit()">Пополнить</button>
          </div>
          <div class="card">
            <h3>Снять</h3>
            <div class="muted">Иногда даже работает!</div>
            <input type="number" id="withdraw-amount" placeholder="Сумма, ₽" min="1">
            <button class="btn btn-ghost" onclick="doWithdraw()">Снять</button>
          </div>
        </div>
        <div class="card">
          <h3>История операций</h3>
          <ul class="tx-list" id="tx-list"><li class="muted">Загрузка...</li></ul>
        </div>
      </section>

      <section class="page" id="page-transfer">
        <div class="card">
          <h3>Перевод по UID</h3>
          <div class="muted">Введите UID получателя (4 цифры).</div>
          <input type="number" id="transfer-uid" placeholder="UID получателя" min="1000" max="9999">
          <input type="number" id="transfer-amount" placeholder="Сумма, ₽" min="1">
          <button class="btn" onclick="doTransfer()">Перевести</button>
        </div>
      </section>

      <section class="page" id="page-chat">
        <div class="card chat-card">
          <h3>Общий чат</h3>
          <div class="chat-messages" id="chat-messages"></div>
          <div class="chat-input-row">
            <input type="text" id="chat-input" placeholder="Написать сообщение..." onkeydown="if(event.key==='Enter')sendChat()">
            <button class="btn" onclick="sendChat()">Отправить</button>
          </div>
        </div>
      </section>

      <section class="page" id="page-about">
        <div class="card">
          <h3>О нас</h3>
          <div class="muted">Команда ПБК Wallet</div>
          <div class="team-grid" id="team-grid"></div>
        </div>
      </section>

      <section class="page" id="page-support">
        <div class="card chat-card">
          <h3>Поддержка</h3>
          <div class="muted">Бот отвечает 24/7 (или никогда)</div>
          <div class="chat-messages" id="support-messages"></div>
          <div class="chat-input-row">
            <input type="text" id="support-input" placeholder="Ваш вопрос..." onkeydown="if(event.key==='Enter')sendSupport()">
            <button class="btn" onclick="sendSupport()">Отправить</button>
          </div>
        </div>
      </section>

      <section class="page" id="page-settings">
        <div class="card">
          <h3>Настройки</h3>
          <div class="settings-row">
            <div><div class="settings-label">Тема оформления</div><div class="settings-desc">Светлая, тёмная, системная или графит</div></div>
            <div class="settings-control">
              <select id="setting-theme" onchange="applyTheme(this.value)">
                <option value="light">☀️ Светлая</option>
                <option value="dark">🌙 Тёмная</option>
                <option value="system">💻 Системная</option>
                <option value="graphite">⬛ Графит</option>
              </select>
            </div>
          </div>
          <div class="settings-row">
            <div><div class="settings-label">Язык интерфейса</div><div class="settings-desc">Русский или English</div></div>
            <div class="settings-control">
              <select id="setting-lang" onchange="applyLang(this.value)">
                <option value="ru">🇷🇺 Русский</option>
                <option value="en">🇬🇧 English</option>
              </select>
            </div>
          </div>
          <div class="settings-row">
            <div><div class="settings-label">Жидкое стекло</div><div class="settings-desc">Полупрозрачные панели с размытием</div></div>
            <label class="switch">
              <input type="checkbox" id="setting-glass" onchange="toggleGlass(this.checked)">
              <span class="slider"></span>
            </label>
          </div>
        </div>
      </section>

      <section class="page" id="page-profile">
        <div class="card">
          <h3>Профиль</h3>
          <div class="profile-row">
            <div class="profile-avatar-big" id="profile-avatar">👤</div>
            <div>
              <div class="profile-username" id="profile-username">—</div>
              <div class="muted" style="margin:4px 0 0;">UID: <span id="profile-uid">#—</span></div>
            </div>
          </div>
          <h4 style="margin-bottom:6px;">Сменить ник</h4>
          <div class="muted">3–20 символов, только уникальный</div>
          <input type="text" id="new-username" placeholder="Новый ник" minlength="3" maxlength="20">
          <button class="btn" onclick="changeUsername()">Сохранить ник</button>
          <h4 style="margin: 20px 0 6px;">Выбор аватара</h4>
          <div class="muted">Из готовых или загрузите свою картинку</div>
          <div class="avatar-grid" id="avatar-grid"></div>
          <div class="avatar-upload-row">
            <input type="file" id="avatar-file" accept="image/*" onchange="uploadAvatar(event)">
            <label for="avatar-file" class="avatar-upload-label">📁 Загрузить свою картинку</label>
          </div>
          <button class="btn btn-danger" onclick="logout()" style="margin-top: 20px;">Выйти из аккаунта</button>
        </div>
      </section>
    </div>
  </main>
</div>

<div id="toast"></div>
<script>
const TEAM = [
  { name: "Takayo", role: "CEO", avatar: "__AVATAR_TAKAYO__" },
  { name: "Sandgar", role: "CTO", avatar: "__AVATAR_SANDGAR__" },
  { name: "Лазарет 21 🇯🇲", role: "Дизайнер", avatar: "__AVATAR_LAZARET__" }
];

function showToast(msg, type) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'show ' + (type || '');
  clearTimeout(el._t);
  el._t = setTimeout(() => el.className = '', 3200);
}

function resolveTheme(theme) {
  if (theme === "system") {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  return theme;
}
function applyTheme(theme) {
  localStorage.setItem("pbk-theme", theme);
  document.documentElement.setAttribute("data-theme", resolveTheme(theme));
  const sel = document.getElementById("setting-theme");
  if (sel) sel.value = theme;
  updateThemeIcons();
}
function toggleTheme() {
  const cur = localStorage.getItem("pbk-theme") || "light";
  const next = (cur === "dark" || cur === "graphite") ? "light" : "dark";
  applyTheme(next);
}
function updateThemeIcons() {
  const cur = localStorage.getItem("pbk-theme") || "light";
  const icon = (cur === "dark" || cur === "graphite") ? "☀️" : "🌙";
  const a = document.getElementById('theme-toggle-auth');
  const b = document.getElementById('theme-toggle-app');
  if (a) a.textContent = icon;
  if (b) b.textContent = icon;
}
function applyLang(lang) { localStorage.setItem("pbk-lang", lang); }
function toggleGlass(on) {
  localStorage.setItem("pbk-glass", on ? "1" : "0");
  document.body.classList.toggle("glass", on);
}

const API = '';
function getToken() { return localStorage.getItem('pbk-token'); }
function setToken(t) { localStorage.setItem('pbk-token', t); }
function clearToken() { localStorage.removeItem('pbk-token'); }

async function api(url, opts) {
  opts = opts || {};
  opts.headers = opts.headers || {};
  const tok = getToken();
  if (tok) opts.headers['Authorization'] = 'Bearer ' + tok;
  if (opts.body && !(opts.body instanceof FormData) && typeof opts.body === 'object') {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(opts.body);
  }
  const res = await fetch(API + url, opts);
  if (res.status === 401) { clearToken(); showAuth(); throw new Error('unauthorized'); }
  return res;
}

function switchTab(which) {
  document.getElementById('tab-login').classList.toggle('active', which === 'login');
  document.getElementById('tab-register').classList.toggle('active', which === 'register');
  document.getElementById('form-login').classList.toggle('hidden', which !== 'login');
  document.getElementById('form-register').classList.toggle('hidden', which !== 'register');
}

async function doRegister(e) {
  e.preventDefault();
  const username = document.getElementById('reg-username').value.trim();
  const p1 = document.getElementById('reg-password').value;
  const p2 = document.getElementById('reg-password2').value;
  if (p1 !== p2) { showToast('Пароли не совпадают', 'error'); return; }
  if (p1.length < 3 || p1.length > 20) { showToast('Пароль: 3–20 символов', 'error'); return; }
  const device_hash = await getDeviceFingerprint();
  const res = await fetch('/api/register', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username, password: p1, device_hash})
  });
  const data = await res.json();
  if (!res.ok) { showToast(data.detail || 'Ошибка', 'error'); return; }
  setToken(data.access_token);
  showToast('Добро пожаловать! UID: #' + data.uid, 'success');
  setTimeout(() => { showApp(); }, 500);
}

async function doLogin(e) {
  e.preventDefault();
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;
  const body = new URLSearchParams();
  body.append('username', username);
  body.append('password', password);
  const res = await fetch('/api/login', {method: 'POST', body});
  const data = await res.json();
  if (!res.ok) { showToast(data.detail || 'Ошибка входа', 'error'); return; }
  setToken(data.access_token);
  showToast('Успешный вход', 'success');
  setTimeout(() => { showApp(); }, 400);
}

function logout() {
  clearToken();
  if (ws) { try { ws.close(); } catch(e){} ws = null; }
  showAuth();
}

function showAuth() {
  document.getElementById('auth-screen').classList.remove('hidden');
  document.getElementById('app-screen').classList.add('hidden');
}

async function showApp() {
  document.getElementById('auth-screen').classList.add('hidden');
  document.getElementById('app-screen').classList.remove('hidden');
  await loadMe();
  await loadTransactions();
  await loadChat();
  renderAvatarGrid();
  renderTeam();
  updateThemeIcons();
  document.getElementById("setting-theme").value = localStorage.getItem("pbk-theme") || "light";
  document.getElementById("setting-lang").value = localStorage.getItem("pbk-lang") || "ru";
  const glass = localStorage.getItem("pbk-glass") === "1";
  document.getElementById("setting-glass").checked = glass;
  document.body.classList.toggle("glass", glass);
}

function switchPage(name) {
  document.querySelectorAll('.nav-item').forEach(el => el.classList.toggle('active', el.dataset.page === name));
  document.querySelectorAll('.page').forEach(el => el.classList.toggle('active', el.id === 'page-' + name));
  if (name === 'chat') setTimeout(scrollChatBottom, 60);
  if (name === 'support') setTimeout(scrollSupportBottom, 60);
}

async function loadMe() {
  const res = await api('/api/me');
  const d = await res.json();
  document.getElementById('balance').textContent = d.balance.toFixed(2) + ' ₽';
  document.getElementById('wallet-uid').textContent = '#' + d.uid;
  document.getElementById('top-username').textContent = d.username;
  document.getElementById('top-avatar').textContent = (d.avatar && d.avatar.length <= 4) ? d.avatar : '👤';
  document.getElementById('top-uid').textContent = '#' + d.uid;
  document.getElementById('profile-username').textContent = d.username;
  document.getElementById('profile-uid').textContent = '#' + d.uid;
  window._currentAvatar = d.avatar;
  updateProfileAvatar(d.avatar);
}
function updateProfileAvatar(av) {
  const el = document.getElementById('profile-avatar');
  if (!el) return;
  if (av && av.startsWith('data:image')) el.innerHTML = '<img src="' + av + '">';
  else el.textContent = av || '👤';
}

async function doDeposit() {
  const amt = parseFloat(document.getElementById('deposit-amount').value);
  if (!amt || amt <= 0) { showToast('Введите сумму', 'error'); return; }
  const res = await api('/api/deposit', {method:'POST', body: {amount: amt}});
  const d = await res.json();
  if (!res.ok) { showToast(d.detail || 'Ошибка', 'error'); return; }
  showToast(d.message, 'success');
  document.getElementById('deposit-amount').value = '';
  await loadMe();
  await loadTransactions();
}

async function doWithdraw() {
  const amt = parseFloat(document.getElementById('withdraw-amount').value);
  if (!amt || amt <= 0) { showToast('Введите сумму', 'error'); return; }
  const res = await api('/api/withdraw', {method:'POST', body: {amount: amt}});
  const d = await res.json();
  showToast(d.message, 'error');
  document.getElementById('withdraw-amount').value = '';
  await loadTransactions();
}

async function loadTransactions() {
  const res = await api('/api/transactions');
  const list = await res.json();
  const ul = document.getElementById('tx-list');
  if (!list.length) { ul.innerHTML = '<li class="muted">Пока пусто</li>'; return; }
  ul.innerHTML = list.map(t => {
    const plus = ['deposit','bonus','transfer_in'].includes(t.type);
    const cls = plus ? 'plus' : 'minus';
    const sign = plus ? '+' : '';
    return `<li><div><div>${escapeHtml(t.comment)}</div><div class="tx-comment">${t.created_at}</div></div><div class="tx-amount ${cls}">${sign}${t.amount}₽</div></li>`;
  }).join('');
}

async function doTransfer() {
  const uid = parseInt(document.getElementById('transfer-uid').value);
  const amt = parseFloat(document.getElementById('transfer-amount').value);
  if (!uid || !amt || amt <= 0) { showToast('Заполните все поля', 'error'); return; }
  const res = await api('/api/transfer', {method:'POST', body: {to_uid: uid, amount: amt}});
  const d = await res.json();
  if (!res.ok) { showToast(d.detail || 'Ошибка', 'error'); return; }
  showToast(d.message, 'success');
  document.getElementById('transfer-uid').value = '';
  document.getElementById('transfer-amount').value = '';
  await loadMe();
  await loadTransactions();
}

let ws = null;

async function loadChat() {
  try {
    const res = await api('/api/messages');
    const list = await res.json();
    const box = document.getElementById('chat-messages');
    box.innerHTML = '';
    list.forEach(m => {
      const div = document.createElement('div');
      div.textContent = `[${m.created_at}] ${m.username}: ${m.text}`;
      box.appendChild(div);
    });
    scrollChatBottom();
  } catch(e) {}
  connectWS();
}

function connectWS() {
  if (ws) return;
  const tok = getToken();
  if (!tok) return;
  const url = (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws/chat?token=' + encodeURIComponent(tok);
  try { ws = new WebSocket(url); } catch(e) { return; }
  ws.onmessage = (ev) => {
    const box = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.textContent = ev.data;
    box.appendChild(div);
    scrollChatBottom();
  };
  ws.onclose = () => { ws = null; };
  ws.onerror = () => {};
}

function sendChat() {
  const inp = document.getElementById('chat-input');
  const text = inp.value.trim();
  if (!text) return;
  if (!ws || ws.readyState !== 1) { showToast('Нет соединения...', 'error'); connectWS(); return; }
  ws.send(text);
  inp.value = '';
}

function scrollChatBottom() {
  const box = document.getElementById('chat-messages');
  if (box) box.scrollTop = box.scrollHeight;
}

async function sendSupport() {
  const inp = document.getElementById('support-input');
  const text = inp.value.trim();
  if (!text) return;
  addSupportMsg('Вы: ' + text);
  inp.value = '';
  const res = await api('/api/support', {method:'POST', body: {message: text}});
  const d = await res.json();
  addSupportMsg('Поддержка: ' + d.reply);
}
function addSupportMsg(text) {
  const box = document.getElementById('support-messages');
  const div = document.createElement('div');
  div.textContent = text;
  box.appendChild(div);
  scrollSupportBottom();
}
function scrollSupportBottom() {
  const box = document.getElementById('support-messages');
  if (box) box.scrollTop = box.scrollHeight;
}

const AVATARS = ['👤','🏦','💠','🅿️','🦊','🐼','🐸','🦉','🐙','🦄','🐧','🐯'];
function renderAvatarGrid() {
  const grid = document.getElementById('avatar-grid');
  grid.innerHTML = '';
  AVATARS.forEach(a => {
    const b = document.createElement('button');
    b.className = 'avatar-option' + (a === window._currentAvatar ? ' selected' : '');
    b.textContent = a;
    b.onclick = () => setAvatar(a);
    grid.appendChild(b);
  });
}
async function setAvatar(a) {
  const res = await api('/api/avatar', {method:'POST', body: {avatar: a}});
  const d = await res.json();
  if (!res.ok) { showToast(d.detail || 'Ошибка', 'error'); return; }
  window._currentAvatar = a;
  updateProfileAvatar(a);
  document.getElementById('top-avatar').textContent = a;
  renderAvatarGrid();
  showToast('Аватар обновлён', 'success');
}

async function uploadAvatar(e) {
  const file = e.target.files[0];
  if (!file) return;
  if (file.size > 2 * 1024 * 1024) { showToast('Файл больше 2 МБ', 'error'); return; }
  const reader = new FileReader();
  reader.onload = async () => {
    const dataUrl = reader.result;
    const res = await api('/api/avatar', {method:'POST', body: {avatar: dataUrl}});
    const d = await res.json();
    if (!res.ok) { showToast(d.detail || 'Ошибка', 'error'); return; }
    window._currentAvatar = dataUrl;
    updateProfileAvatar(dataUrl);
    document.getElementById('top-avatar').textContent = '👤';
    renderAvatarGrid();
    showToast('Аватар загружен', 'success');
  };
  reader.readAsDataURL(file);
}

async function changeUsername() {
  const newName = document.getElementById('new-username').value.trim();
  if (newName.length < 3 || newName.length > 20) { showToast('Ник: 3–20 символов', 'error'); return; }
  const res = await api('/api/username', {method:'POST', body: {username: newName}});
  const d = await res.json();
  if (!res.ok) { showToast(d.detail || 'Ошибка', 'error'); return; }
  setToken(d.access_token);
  document.getElementById('new-username').value = '';
  showToast('Ник изменён', 'success');
  await loadMe();
}

function renderTeam() {
  const grid = document.getElementById('team-grid');
  if (!grid) return;
  grid.innerHTML = TEAM.map(m => `
    <div class="team-card">
      <img class="team-avatar" src="${m.avatar}" alt="${escapeHtml(m.name)}">
      <div class="team-name">${escapeHtml(m.name)}</div>
      <div class="team-role">${escapeHtml(m.role)}</div>
    </div>
  `).join('');
}

async function getDeviceFingerprint() {
  const parts = [
    navigator.userAgent, navigator.language,
    screen.width + 'x' + screen.height,
    screen.colorDepth,
    new Date().getTimezoneOffset(),
    navigator.hardwareConcurrency || 0,
    navigator.platform || ''
  ];
  try {
    const c = document.createElement('canvas');
    const ctx = c.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillStyle = '#f60';
    ctx.fillRect(125,1,62,20);
    ctx.fillStyle = '#069';
    ctx.fillText('PBK-Wallet', 2, 15);
    parts.push(c.toDataURL());
  } catch(e) {}
  const str = parts.join('|');
  const buf = new TextEncoder().encode(str);
  const hash = await crypto.subtle.digest('SHA-256', buf);
  return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2,'0')).join('');
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

document.addEventListener('DOMContentLoaded', () => {
  applyTheme(localStorage.getItem("pbk-theme") || "light");
  const glass = localStorage.getItem("pbk-glass") === "1";
  document.body.classList.toggle("glass", glass);
  updateThemeIcons();
  if (getToken()) showApp();
  else showAuth();
});
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
  if (localStorage.getItem("pbk-theme") === "system") {
    document.documentElement.setAttribute("data-theme", resolveTheme("system"));
  }
});
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def root():
    html = INDEX_HTML
    html = html.replace("__AVATAR_TAKAYO__", AVATAR_TAKAYO)
    html = html.replace("__AVATAR_SANDGAR__", AVATAR_SANDGAR)
    html = html.replace("__AVATAR_LAZARET__", AVATAR_LAZARET)
    return html

if __name__ == "__main__":
    multiprocessing.freeze_support()
    print("=" * 50)
    print("  PBK Wallet")
    print(f"  http://127.0.0.1:{PORT}")
    if USE_POSTGRES:
        print("  База: PostgreSQL")
    else:
        print("  База: SQLite (локально)")
    print("=" * 50)
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=PORT, reload=False, workers=1)