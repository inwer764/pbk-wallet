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
# ---- Аватарки авторов ----
try:
    from avatars import AVATAR_TAKAYO, AVATAR_SANDGAR, AVATAR_LAZARET
except ImportError:
    AVATAR_TAKAYO = "👤"
    AVATAR_SANDGAR = "👤"
    AVATAR_LAZARET = "👤"

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# ============ НАСТРОЙКИ ============
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24 * 7
PORT = int(os.environ.get("PORT", 8000))
DATABASE_URL = os.environ.get("DATABASE_URL", "")

USE_POSTGRES = DATABASE_URL.startswith("postgres")

if USE_POSTGRES:
    import psycopg2
else:
    import sqlite3

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SQLITE_PATH = os.path.join(BASE_DIR, "pbk.db")

# ============ БД ============
def get_db():
    if USE_POSTGRES:
        return psycopg2.connect(DATABASE_URL)
    return sqlite3.connect(SQLITE_PATH)

def ph(query: str) -> str:
    if USE_POSTGRES:
        return query.replace("?", "%s")
    return query

# ============ ХЭШ ============
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

# ============ БАЗА ============
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
            device_type TEXT DEFAULT 'unknown',
            device_browser TEXT DEFAULT 'unknown',
            device_os TEXT DEFAULT 'unknown',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            device_type TEXT DEFAULT 'unknown',
            device_browser TEXT DEFAULT 'unknown',
            device_os TEXT DEFAULT 'unknown',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    if user:
        c.execute(ph("UPDATE users SET last_seen=CURRENT_TIMESTAMP WHERE id=?"), (user[0],))
        conn.commit()
    conn.close()
    if not user:
        raise exc
    return {"id": user[0], "uid": user[1], "username": user[2],
            "balance": user[3], "hamster_coins": user[4], "avatar": user[5]}

def is_admin(user):
    return user.get("uid") == 1111

def generate_uid():
    conn = get_db()
    c = conn.cursor()
    for _ in range(10000):
        uid = random.randint(1000, 9999)
        if uid == 1111:
            continue
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
    device_type: str = "unknown"
    device_browser: str = "unknown"
    device_os: str = "unknown"

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

class AdminMoneyData(BaseModel):
    uid: int
    amount: float

# ============ APP ============
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="ПБК Wallet", lifespan=lifespan)

# ============ WS ============
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

    # UID 1111 только для takayo
    if data.username.lower() == "takayo":
        c.execute(ph("SELECT id FROM users WHERE uid=?"), (1111,))
        if c.fetchone():
            conn.close()
            raise HTTPException(400, "UID 1111 уже занят")
        uid = 1111
    else:
        uid = generate_uid()

    hashed = hash_password(data.password)

    if USE_POSTGRES:
        c.execute(
            "INSERT INTO users (uid, username, hashed_password, device_hash, avatar, device_type, device_browser, device_os) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (uid, data.username, hashed, data.device_hash or None, "👤", data.device_type, data.device_browser, data.device_os)
        )
        user_id = c.fetchone()[0]
    else:
        c.execute(
            "INSERT INTO users (uid, username, hashed_password, device_hash, avatar, device_type, device_browser, device_os) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (uid, data.username, hashed, data.device_hash or None, "👤", data.device_type, data.device_browser, data.device_os)
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
            "hamster_coins": current["hamster_coins"], "avatar": current["avatar"],
            "is_admin": is_admin(current)}

@app.post("/api/tap")
def tap(current=Depends(get_current_user)):
    TAP_REWARD = 2
    conn = get_db()
    c = conn.cursor()
    c.execute(ph("UPDATE users SET balance = balance + ? WHERE id=?"), (TAP_REWARD, current["id"]))
    c.execute(ph("INSERT INTO transactions (user_id, type, amount, comment) VALUES (?, ?, ?, ?)"),
              (current["id"], "tap", TAP_REWARD, f"Тап +{TAP_REWARD}₽"))
    conn.commit()
    c.execute(ph("SELECT balance FROM users WHERE id=?"), (current["id"],))
    new_balance = c.fetchone()[0]
    c.execute(ph("SELECT COUNT(*) FROM transactions WHERE user_id=? AND type='tap'"), (current["id"],))
    total_taps = c.fetchone()[0]
    conn.close()
    return {"message": f"+{TAP_REWARD}₽", "balance": new_balance, "total_taps": total_taps}

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
              (current["id"], "transfer_out", data.amount, f"Перевод #{data.to_uid} ({recipient[1]})"))
    c.execute(ph("INSERT INTO transactions (user_id, type, amount, comment) VALUES (?, ?, ?, ?)"),
              (recipient[0], "transfer_in", data.amount, f"Перевод от #{current['uid']} ({current['username']})"))
    conn.commit()
    c.execute(ph("SELECT balance FROM users WHERE id=?"), (current["id"],))
    new_balance = c.fetchone()[0]
    conn.close()
    return {"message": f"Переведено {data.amount}₽ пользователю #{data.to_uid}", "balance": new_balance}

@app.get("/api/transactions")
def transactions(current=Depends(get_current_user)):
    conn = get_db()
    c = conn.cursor()
    c.execute(ph("SELECT type, amount, comment, created_at FROM transactions WHERE user_id=? ORDER BY created_at DESC LIMIT 100"), (current["id"],))
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
        "тап": "Тапай монетку в кошельке — +3₽ за тап!",
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
    if new_name.lower() == "takayo":
        raise HTTPException(400, "Этот ник зарезервирован")
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
    c.execute("SELECT user_id, username, text, created_at FROM messages ORDER BY created_at DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    return [{"user_id": r[0], "username": r[1], "text": r[2], "created_at": str(r[3])} for r in reversed(rows)]

# ============ ADMIN ============
@app.get("/api/admin/users")
def admin_users(current=Depends(get_current_user)):
    if not is_admin(current):
        raise HTTPException(403, "Доступ запрещён")
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT uid, username, balance, avatar, device_type, device_browser, device_os, created_at, last_seen FROM users ORDER BY uid ASC")
    rows = c.fetchall()
    conn.close()
    return [{
        "uid": r[0], "username": r[1], "balance": round(r[2], 2),
        "avatar": r[3], "device_type": r[4], "device_browser": r[5],
        "device_os": r[6], "created_at": str(r[7]), "last_seen": str(r[8])
    } for r in rows]

@app.post("/api/admin/give-money")
def admin_give_money(data: AdminMoneyData, current=Depends(get_current_user)):
    if not is_admin(current):
        raise HTTPException(403, "Доступ запрещён")
    if data.amount == 0:
        raise HTTPException(400, "Сумма не может быть нулевой")
    conn = get_db()
    c = conn.cursor()
    c.execute(ph("SELECT id, username FROM users WHERE uid=?"), (data.uid,))
    target = c.fetchone()
    if not target:
        conn.close()
        raise HTTPException(404, "Пользователь не найден")
    c.execute(ph("UPDATE users SET balance = balance + ? WHERE id=?"), (data.amount, target[0]))
    sign = "+" if data.amount > 0 else ""
    c.execute(ph("INSERT INTO transactions (user_id, type, amount, comment) VALUES (?, ?, ?, ?)"),
              (target[0], "admin_gift", data.amount, f"От админа: {sign}{data.amount}₽"))
    conn.commit()
    conn.close()
    return {"message": f"Пользователю #{data.uid} начислено {sign}{data.amount}₽"}

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
    c.execute("SELECT username, text, created_at FROM messages ORDER BY created_at DESC LIMIT 30")
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
            c.execute(ph("INSERT INTO messages (user_id, username, text) VALUES (?, ?, ?)"), (user[0], user[1], data))
            conn.commit()
            conn.close()
            await manager.broadcast(f"[{datetime.now().strftime('%H:%M')}] {user[1]}: {data}")
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

# ============ ФРОНТЕНД ============
from index import INDEX_HTML

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
    print("=" * 50)
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=PORT, reload=False, workers=1)