# QUVVAT.MARKET API

Bu papka `index.html` uchun ishlaydigan Python backend API ni beradi.

## Ishga tushirish

1. Virtual environment yarating:
   - `python -m venv .venv`
2. Aktivatsiya qiling (PowerShell):
   - `.venv\Scripts\Activate.ps1`
3. Kutubxonalarni o'rnating:
   - `pip install -r api_server/requirements.txt`
4. API ni ishga tushiring:
   - `python api_server/app.py`

Server `http://127.0.0.1:5000` da ishlaydi.

## Environment (ixtiyoriy)

`.env` faylida:

- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` (OTP email uchun)
- `CARD_VERIFY_URL`, `CARD_VERIFY_KEY` (real karta verifikatsiya provider)
- `PASSPORT_VERIFY_URL`, `PASSPORT_VERIFY_KEY` (real pasport verifikatsiya provider)

Provider kalitlar bo'lmasa backend offline fallback validatsiya qiladi.

## Endpointlar

- `POST /api/auth/login`
- `POST /api/auth/register`
- `POST /api/auth/verify-otp`
- `POST /api/auth/logout`
- `GET /api/products`
- `POST /api/products` (admin)
- `POST /api/favorites/toggle`
- `GET /api/favorites`
- `POST /api/verify/card`
- `POST /api/verify/passport`
- `GET /api/orders`
- `POST /api/orders`
- `GET /api/activity` (admin)
- `POST /api/contact`
- `GET /api/health`
