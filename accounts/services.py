"""OTP yuborish (sessiya orqali, console+frontendga auto-fill)."""
from __future__ import annotations

import random
from django.utils import timezone


SIGNATURE = "sherjonov abduaziz"
OTP_TTL_SECONDS = 10 * 60


def generate_otp() -> str:
    return f"{random.randint(0, 999999):06d}"


def issue_otp(session, purpose: str, payload: dict) -> str:
    code = generate_otp()
    session[f"otp_{purpose}"] = {
        "code": code,
        "payload": payload,
        "issued_at": timezone.now().isoformat(),
    }
    session.modified = True
    print("\n" + "=" * 60)
    print(f"[EMAIL] To: {payload.get('email', '<unknown>')}")
    print(f"[EMAIL] Subject: Tasdiqlash kodi ({purpose})")
    print(f"[EMAIL] Code: {code}")
    print(f"[EMAIL] -- {SIGNATURE}")
    print("=" * 60 + "\n", flush=True)
    return code


def consume_otp(session, purpose: str, code: str):
    bucket = session.get(f"otp_{purpose}")
    if not bucket:
        return None
    if str(bucket.get("code")) != str(code).strip():
        return None
    issued = bucket.get("issued_at")
    if issued:
        try:
            ts = timezone.datetime.fromisoformat(issued)
            if (timezone.now() - ts).total_seconds() > OTP_TTL_SECONDS:
                session.pop(f"otp_{purpose}", None)
                return None
        except Exception:
            pass
    payload = bucket.get("payload", {})
    session.pop(f"otp_{purpose}", None)
    session.modified = True
    return payload


def peek_otp(session, purpose: str):
    bucket = session.get(f"otp_{purpose}")
    if not bucket:
        return None
    return bucket.get("code")
