"""QUVVAT Market production-style API."""

from __future__ import annotations

import hashlib
import os
import random
import re
import secrets
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from products import PRODUCTS
from store import load_json, save_json

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
app = Flask(__name__, static_folder=str(ROOT), static_url_path="")
CORS(app)

TOKENS: dict[str, int] = {}

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
OTP_SIGNATURE = "Sherjonov Abduaziz"

CARD_VERIFY_URL = os.environ.get("CARD_VERIFY_URL", "")
CARD_VERIFY_KEY = os.environ.get("CARD_VERIFY_KEY", "")
PASSPORT_VERIFY_URL = os.environ.get("PASSPORT_VERIFY_URL", "")
PASSPORT_VERIFY_KEY = os.environ.get("PASSPORT_VERIFY_KEY", "")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def hash_pass(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def safe_user(user: dict) -> dict:
    return {
        "id": user["id"],
        "name": user["name"],
        "surname": user["surname"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
    }


def init_data() -> None:
    users = load_json("users", [])
    if not users:
        users = [
            {
                "id": 1,
                "name": "Abduaziz",
                "surname": "Sherjonov",
                "username": "Sherjonov",
                "email": "abduazizsherjonov7@gmail.com",
                "password_hash": hash_pass("abushka2011"),
                "role": "admin",
                "created_at": now_iso(),
            }
        ]
        save_json("users", users)
    if not load_json("products", []):
        save_json("products", PRODUCTS)
    for table_name in ("orders", "activity", "otps", "favorites"):
        if load_json(table_name, None) is None:
            save_json(table_name, [] if table_name != "otps" else {})


def get_users() -> list[dict]:
    return load_json("users", [])


def log_activity(user: dict, action: str) -> None:
    activity = load_json("activity", [])
    activity.insert(
        0,
        {
            "id": len(activity) + 1,
            "full_name": f"{user['name']} {user['surname']}".strip(),
            "username": user["username"],
            "email": user["email"],
            "action": action,
            "time": now_iso(),
        },
    )
    save_json("activity", activity[:500])


def auth_user() -> dict | None:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.removeprefix("Bearer ").strip()
    user_id = TOKENS.get(token)
    if not user_id:
        return None
    return next((u for u in get_users() if u["id"] == user_id), None)


def send_otp_email(email: str, code: str) -> bool:
    if not SMTP_USER or not SMTP_PASS:
        return False
    subject = "QUVVAT Market tasdiqlash kodi"
    body = f"Salom.\nTasdiqlash kodi: {code}\nImzo: {OTP_SIGNATURE}"
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = email
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [email], msg.as_string())
        return True
    except Exception:
        return False


def detect_card_brand(card: str) -> str:
    if card.startswith("8600"):
        return "Uzcard"
    if card.startswith("9860"):
        return "Humo"
    if card.startswith("4"):
        return "Visa"
    if card[:2] in {"51", "52", "53", "54", "55"}:
        return "Mastercard"
    return "Unknown"


def luhn_ok(card_number: str) -> bool:
    digits = [int(ch) for ch in card_number if ch.isdigit()]
    if len(digits) != 16:
        return False
    checksum = 0
    parity = len(digits) % 2
    for index, digit in enumerate(digits):
        value = digit * 2 if index % 2 == parity else digit
        checksum += value - 9 if value > 9 else value
    return checksum % 10 == 0


def verify_card_external(payload: dict) -> tuple[bool, str]:
    if not CARD_VERIFY_URL or not CARD_VERIFY_KEY:
        return luhn_ok(payload["card_number"]), "offline-check"
    try:
        response = requests.post(
            CARD_VERIFY_URL,
            headers={"Authorization": f"Bearer {CARD_VERIFY_KEY}"},
            json=payload,
            timeout=8,
        )
        data = response.json()
        return bool(data.get("valid")), "provider-check"
    except Exception:
        return luhn_ok(payload["card_number"]), "fallback-offline"


def verify_passport_external(payload: dict) -> tuple[bool, str]:
    serial = payload.get("serial", "")
    number = payload.get("number", "")
    pinfl = payload.get("pinfl", "")
    offline_valid = (
        bool(re.fullmatch(r"[A-Z]{2}", serial))
        and bool(re.fullmatch(r"\d{7}", number))
        and bool(re.fullmatch(r"\d{14}", pinfl))
    )
    if not PASSPORT_VERIFY_URL or not PASSPORT_VERIFY_KEY:
        return offline_valid, "offline-check"
    try:
        response = requests.post(
            PASSPORT_VERIFY_URL,
            headers={"Authorization": f"Bearer {PASSPORT_VERIFY_KEY}"},
            json=payload,
            timeout=8,
        )
        data = response.json()
        return bool(data.get("valid")), "provider-check"
    except Exception:
        return offline_valid, "fallback-offline"


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "service": "quvvat-market", "time": now_iso()})


@app.post("/api/auth/register")
def register():
    body = request.get_json(silent=True) or {}
    required = ["name", "surname", "username", "email", "password"]
    if any(not str(body.get(key, "")).strip() for key in required):
        return jsonify({"error": "Barcha maydonlar majburiy"}), 400

    users = get_users()
    username = body["username"].strip()
    email = body["email"].strip().lower()
    if any(u["username"].lower() == username.lower() for u in users):
        return jsonify({"error": "Bu username band"}), 409
    if any(u["email"].lower() == email for u in users):
        return jsonify({"error": "Bu email allaqachon mavjud"}), 409

    code = f"{random.randint(100000, 999999)}"
    otps = load_json("otps", {})
    otps[email] = {
        "code": code,
        "payload": {
            "name": body["name"].strip(),
            "surname": body["surname"].strip(),
            "username": username,
            "email": email,
            "password_hash": hash_pass(body["password"]),
        },
        "created_at": now_iso(),
    }
    save_json("otps", otps)
    sent = send_otp_email(email, code)
    return jsonify({"ok": True, "signature": OTP_SIGNATURE, "dev_otp": code, "email_sent": sent})


@app.post("/api/auth/verify-otp")
def verify_otp():
    body = request.get_json(silent=True) or {}
    email = str(body.get("email", "")).strip().lower()
    code = str(body.get("code", "")).strip()
    otps = load_json("otps", {})
    current = otps.get(email)
    if not current or current.get("code") != code:
        return jsonify({"error": "OTP noto'g'ri"}), 400

    users = get_users()
    payload = current["payload"]
    user = {
        "id": max((u["id"] for u in users), default=0) + 1,
        "name": payload["name"],
        "surname": payload["surname"],
        "username": payload["username"],
        "email": payload["email"],
        "password_hash": payload["password_hash"],
        "role": "user",
        "created_at": now_iso(),
    }
    users.append(user)
    save_json("users", users)
    otps.pop(email, None)
    save_json("otps", otps)
    log_activity(user, "register")

    token = secrets.token_urlsafe(32)
    TOKENS[token] = user["id"]
    return jsonify({"token": token, "user": safe_user(user)})


@app.post("/api/auth/login")
def login():
    body = request.get_json(silent=True) or {}
    username = str(body.get("username", "")).strip()
    password = str(body.get("password", ""))
    user = next(
        (
            u
            for u in get_users()
            if u["username"].lower() == username.lower()
            and u["password_hash"] == hash_pass(password)
        ),
        None,
    )
    if not user:
        return jsonify({"error": "Login yoki parol noto'g'ri"}), 401
    log_activity(user, "login")
    token = secrets.token_urlsafe(32)
    TOKENS[token] = user["id"]
    return jsonify({"token": token, "user": safe_user(user)})


@app.post("/api/auth/logout")
def logout():
    user = auth_user()
    if user:
        log_activity(user, "logout")
    return jsonify({"ok": True})


@app.get("/api/products")
def products():
    category = request.args.get("category", "all")
    query = request.args.get("q", "").strip().lower()
    rows = load_json("products", [])
    if category != "all":
        rows = [row for row in rows if row["cat"] == category]
    if query:
        rows = [row for row in rows if row["name"].lower() == query]
    return jsonify(rows)


@app.post("/api/products")
def create_product():
    user = auth_user()
    if not user or user.get("role") != "admin":
        return jsonify({"error": "Faqat admin"}), 403
    body = request.get_json(silent=True) or {}
    required = ["cat", "emoji", "name", "desc", "price"]
    if any(not str(body.get(key, "")).strip() for key in required):
        return jsonify({"error": "Mahsulot ma'lumotlari to'liq emas"}), 400
    rows = load_json("products", [])
    row = {
        "id": max((x["id"] for x in rows), default=0) + 1,
        "cat": body["cat"],
        "emoji": body["emoji"],
        "name": body["name"],
        "desc": body["desc"],
        "price": int(body["price"]),
        "badge": body.get("badge", ""),
        "image": body.get("image", ""),
        "stock": 15,
    }
    rows.append(row)
    save_json("products", rows)
    return jsonify({"ok": True, "product": row}), 201


@app.post("/api/favorites/toggle")
def toggle_favorite():
    user = auth_user()
    if not user:
        return jsonify({"error": "Avval login qiling"}), 401
    body = request.get_json(silent=True) or {}
    product_id = int(body.get("product_id") or 0)
    if not product_id:
        return jsonify({"error": "product_id kerak"}), 400
    rows = load_json("favorites", [])
    key = {"user_id": user["id"], "product_id": product_id}
    exists = next((item for item in rows if item["user_id"] == key["user_id"] and item["product_id"] == key["product_id"]), None)
    if exists:
        rows = [item for item in rows if not (item["user_id"] == key["user_id"] and item["product_id"] == key["product_id"])]
        liked = False
    else:
        rows.append(key)
        liked = True
    save_json("favorites", rows)
    ids = [item["product_id"] for item in rows if item["user_id"] == user["id"]]
    return jsonify({"ok": True, "liked": liked, "ids": ids})


@app.get("/api/favorites")
def favorites():
    user = auth_user()
    if not user:
        return jsonify({"ids": []})
    rows = load_json("favorites", [])
    return jsonify({"ids": [item["product_id"] for item in rows if item["user_id"] == user["id"]]})


@app.post("/api/verify/card")
def verify_card():
    body = request.get_json(silent=True) or {}
    card_number = re.sub(r"\D", "", str(body.get("card_number", "")))
    holder = str(body.get("holder", "")).strip()
    expiry = str(body.get("expiry", "")).strip()
    if len(card_number) != 16 or not holder or not re.fullmatch(r"\d{2}/\d{2}", expiry):
        return jsonify({"valid": False, "error": "Karta format xato"}), 400
    valid, source = verify_card_external({"card_number": card_number, "holder": holder, "expiry": expiry})
    return jsonify({"valid": valid, "brand": detect_card_brand(card_number), "source": source})


@app.post("/api/verify/passport")
def verify_passport():
    body = request.get_json(silent=True) or {}
    valid, source = verify_passport_external(body)
    return jsonify({"valid": valid, "source": source})


@app.get("/api/orders")
def list_orders():
    user = auth_user()
    if not user:
        return jsonify({"error": "Avval login qiling"}), 401
    rows = load_json("orders", [])
    if user["role"] == "admin":
        return jsonify(rows)
    return jsonify([row for row in rows if row["user"]["id"] == user["id"]])


@app.post("/api/orders")
def create_order():
    user = auth_user()
    if not user:
        return jsonify({"error": "Avval login qiling"}), 401
    body = request.get_json(silent=True) or {}
    items = body.get("items", [])
    if not items:
        return jsonify({"error": "Savat bo'sh"}), 400
    for item in items:
        qty = int(item.get("qty", 0))
        if qty < 1 or qty > 15:
            return jsonify({"error": "Har mahsulot 1..15 oralig'ida bo'lishi kerak"}), 400
    orders = load_json("orders", [])
    number = f"QM-{20000 + len(orders) + 1}"
    order = {
        "id": len(orders) + 1,
        "number": number,
        "user": safe_user(user),
        "customer": {
            "name": body.get("name", ""),
            "surname": body.get("surname", ""),
            "email": body.get("email", ""),
            "phone": body.get("phone", ""),
        },
        "address": body.get("address", {}),
        "payment": body.get("payment", {}),
        "passport": body.get("passport", {}),
        "items": items,
        "total": int(body.get("total", 0)),
        "status": "confirmed",
        "created_at": now_iso(),
    }
    orders.insert(0, order)
    save_json("orders", orders)
    return jsonify({"ok": True, "order_number": number, "avg_eta_minutes": 30})


@app.get("/api/activity")
def activity():
    user = auth_user()
    if not user or user["role"] != "admin":
        return jsonify({"error": "Faqat admin"}), 403
    return jsonify(load_json("activity", [])[:300])


@app.post("/api/contact")
def contact():
    body = request.get_json(silent=True) or {}
    message = str(body.get("message", "")).strip()
    if not message:
        return jsonify({"error": "Xabar bo'sh"}), 400
    contacts = load_json("contacts", [])
    contacts.append(
        {
            "id": len(contacts) + 1,
            "name": body.get("name", ""),
            "email": body.get("email", ""),
            "phone": body.get("phone", ""),
            "message": message,
            "created_at": now_iso(),
        }
    )
    save_json("contacts", contacts)
    return jsonify({"ok": True})


@app.get("/")
def index():
    return send_from_directory(ROOT, "index.html")


if __name__ == "__main__":
    init_data()
    app.run(host="127.0.0.1", port=5000, debug=True)
