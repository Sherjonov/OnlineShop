"""Initial DB setup: migrate, create admin Sherjonov, seed categories+products (12+ each).

Run: python scripts/seed.py  (from project root)
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.core.management import call_command

print(">>> makemigrations + migrate ...")
call_command("makemigrations", "accounts", "products", "orders", "core", interactive=False, verbosity=1)
call_command("migrate", interactive=False, verbosity=1)

from django.contrib.auth import get_user_model
from products.models import Category, Product

User = get_user_model()

# ---------- Admin -------------------------------------------------------
ADMIN_USERNAME = "Sherjonov"
ADMIN_PASSWORD = "qwerty123321"
ADMIN_EMAIL = "sherjonov@sayt6.local"

admin = User.objects.filter(username=ADMIN_USERNAME).first()
if admin:
    admin.set_password(ADMIN_PASSWORD)
    admin.email = ADMIN_EMAIL
    admin.first_name = "Abduaziz"
    admin.last_name = "Sherjonov"
    admin.is_staff = True
    admin.is_superuser = True
    admin.is_active = True
    admin.is_email_verified = True
    admin.save()
    print(f">>> Admin updated: {ADMIN_USERNAME}")
else:
    User.objects.create_superuser(
        username=ADMIN_USERNAME,
        email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD,
        first_name="Abduaziz",
        last_name="Sherjonov",
        is_email_verified=True,
    )
    print(f">>> Admin created: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")

# ---------- Categories -------------------------------------------------
CATEGORIES = [
    {"name": "Fast Food", "slug": "fastfood", "icon": "F", "sort_order": 1},
    {"name": "Ichimliklar", "slug": "drinks", "icon": "D", "sort_order": 2},
    {"name": "Milliy taomlar", "slug": "milliy", "icon": "M", "sort_order": 3},
    {"name": "Shirinliklar", "slug": "shirinliklar", "icon": "S", "sort_order": 4},
]
for c in CATEGORIES:
    Category.objects.update_or_create(slug=c["slug"], defaults=c)
print(f">>> Categories: {Category.objects.count()}")

# ---------- Products (12+ per category) --------------------------------
PRODUCTS = [
    # === Fast Food (15 ta) ===
    {"category": "fastfood", "name": "Klassik Burger", "emoji": "🍔", "description": "Mol go'shti, salat, pomidor, sous", "price": 35000, "old_price": 42000, "badge": "hot", "weight": "250g"},
    {"category": "fastfood", "name": "Cheeseburger", "emoji": "🍔", "description": "Ikki qavat pishloq bilan", "price": 39000, "badge": "", "weight": "270g"},
    {"category": "fastfood", "name": "Double Burger", "emoji": "🍔", "description": "Ikki kotlet, maxsus sous", "price": 48000, "badge": "hot", "weight": "350g"},
    {"category": "fastfood", "name": "Chicken Burger", "emoji": "🍔", "description": "Tovuq filesi, salat", "price": 32000, "badge": "new", "weight": "230g"},
    {"category": "fastfood", "name": "Hot-dog Classic", "emoji": "🌭", "description": "Sosiska, ketchup, gorchitsa", "price": 22000, "badge": "", "weight": "180g"},
    {"category": "fastfood", "name": "Hot-dog Premium", "emoji": "🌭", "description": "Ikki sosiska, pishloq", "price": 28000, "badge": "", "weight": "220g"},
    {"category": "fastfood", "name": "Lavash Tovuq", "emoji": "🌯", "description": "Tovuq go'shti va sabzavotlar", "price": 28000, "weight": "300g"},
    {"category": "fastfood", "name": "Lavash Go'sht", "emoji": "🌯", "description": "Mol go'shti, sous", "price": 32000, "weight": "320g"},
    {"category": "fastfood", "name": "Shaurma Mini", "emoji": "🌯", "description": "Kichik shaurma", "price": 18000, "weight": "200g"},
    {"category": "fastfood", "name": "Shaurma Katta", "emoji": "🌯", "description": "Katta shaurma", "price": 35000, "badge": "hot", "weight": "400g"},
    {"category": "fastfood", "name": "Free Kartoshka", "emoji": "🍟", "description": "Qovurilgan kartoshka", "price": 15000, "weight": "150g"},
    {"category": "fastfood", "name": "Kartoshka Katta", "emoji": "🍟", "description": "Katta porsiya", "price": 22000, "weight": "250g"},
    {"category": "fastfood", "name": "Nuggets 6x", "emoji": "🍗", "description": "6 dona tovuq naggets", "price": 25000, "badge": "new", "weight": "180g"},
    {"category": "fastfood", "name": "Nuggets 12x", "emoji": "🍗", "description": "12 dona tovuq naggets", "price": 45000, "weight": "360g"},
    {"category": "fastfood", "name": "Combo Set", "emoji": "🍱", "description": "Burger + Free + Cola", "price": 55000, "old_price": 65000, "badge": "sale", "weight": "550g"},

    # === Ichimliklar (15 ta) ===
    {"category": "drinks", "name": "Coca-Cola 0.5L", "emoji": "🥤", "description": "Sovuq Coca-Cola", "price": 12000, "weight": "500ml", "badge": ""},
    {"category": "drinks", "name": "Coca-Cola 1L", "emoji": "🥤", "description": "Oilaviy hajm", "price": 18000, "weight": "1L"},
    {"category": "drinks", "name": "Fanta 0.5L", "emoji": "🍊", "description": "Apelsin ta'mli", "price": 12000, "weight": "500ml"},
    {"category": "drinks", "name": "Sprite 0.5L", "emoji": "🍋", "description": "Limon-laym", "price": 12000, "weight": "500ml"},
    {"category": "drinks", "name": "Pepsi 0.5L", "emoji": "🥤", "description": "Pepsi ichimlik", "price": 11000, "weight": "500ml"},
    {"category": "drinks", "name": "Mirinda 0.5L", "emoji": "🍊", "description": "Apelsin mirinda", "price": 11000, "weight": "500ml"},
    {"category": "drinks", "name": "Mineral suv", "emoji": "💧", "description": "Sovuq mineral suv", "price": 5000, "weight": "500ml"},
    {"category": "drinks", "name": "Yangi Apelsin", "emoji": "🍹", "description": "100% tabiiy sharbat", "price": 25000, "badge": "new", "weight": "300ml"},
    {"category": "drinks", "name": "Yangi Olma", "emoji": "🍎", "description": "Tabiiy olma sharbati", "price": 22000, "weight": "300ml"},
    {"category": "drinks", "name": "Limonad", "emoji": "🍋", "description": "Uy limonadi", "price": 18000, "badge": "hot", "weight": "400ml"},
    {"category": "drinks", "name": "Mojito", "emoji": "🍸", "description": "Alkogolsiz mojito", "price": 28000, "badge": "new", "weight": "350ml"},
    {"category": "drinks", "name": "Milkshake Shokolad", "emoji": "🥛", "description": "Shokoladli milkshake", "price": 30000, "weight": "400ml"},
    {"category": "drinks", "name": "Milkshake Vanil", "emoji": "🥛", "description": "Vanilli milkshake", "price": 30000, "weight": "400ml"},
    {"category": "drinks", "name": "Kofe Amerikano", "emoji": "☕", "description": "Klassik amerikano", "price": 15000, "weight": "200ml"},
    {"category": "drinks", "name": "Kofe Latte", "emoji": "☕", "description": "Sutli latte", "price": 22000, "badge": "hot", "weight": "300ml"},

    # === Milliy taomlar (15 ta) ===
    {"category": "milliy", "name": "Plov", "emoji": "🍚", "description": "Toshkent palovi", "price": 45000, "badge": "hot", "weight": "400g"},
    {"category": "milliy", "name": "Plov Katta", "emoji": "🍚", "description": "Katta porsiya plov", "price": 60000, "weight": "600g"},
    {"category": "milliy", "name": "Manti 5x", "emoji": "🥟", "description": "5 dona bug' mantisi", "price": 32000, "weight": "350g"},
    {"category": "milliy", "name": "Manti 10x", "emoji": "🥟", "description": "10 dona manti", "price": 58000, "badge": "sale", "old_price": 65000, "weight": "700g"},
    {"category": "milliy", "name": "Lag'mon", "emoji": "🍜", "description": "Qaynoq lag'mon", "price": 30000, "badge": "hot", "weight": "400ml"},
    {"category": "milliy", "name": "Chuchvara", "emoji": "🥟", "description": "Sho'rva bilan", "price": 28000, "weight": "350g"},
    {"category": "milliy", "name": "Somsa Go'sht", "emoji": "🥧", "description": "Tandirda pishgan", "price": 12000, "weight": "150g"},
    {"category": "milliy", "name": "Somsa Tovuq", "emoji": "🥧", "description": "Tovuqli somsa", "price": 14000, "badge": "new", "weight": "150g"},
    {"category": "milliy", "name": "Kabob", "emoji": "🍢", "description": "Mol go'shti kabob", "price": 55000, "badge": "hot", "weight": "300g"},
    {"category": "milliy", "name": "Lyulya Kabob", "emoji": "🍢", "description": "Maydalangan go'sht", "price": 45000, "weight": "250g"},
    {"category": "milliy", "name": "Shashlik 3x", "emoji": "🍖", "description": "3 sikh shashlik", "price": 65000, "weight": "350g"},
    {"category": "milliy", "name": "Norin", "emoji": "🍝", "description": "Milliy norin", "price": 38000, "weight": "350g"},
    {"category": "milliy", "name": "Dimlama", "emoji": "🍲", "description": "Sabzavotli dimlama", "price": 42000, "weight": "450g"},
    {"category": "milliy", "name": "Mastava", "emoji": "🍲", "description": "Guruchli sho'rva", "price": 25000, "weight": "400ml"},
    {"category": "milliy", "name": "Tandir Non", "emoji": "🫓", "description": "Issiq tandir non", "price": 5000, "weight": "200g"},

    # === Shirinliklar (15 ta) ===
    {"category": "shirinliklar", "name": "Tiramisu", "emoji": "🍰", "description": "Italyancha klassik", "price": 45000, "badge": "new", "weight": "150g"},
    {"category": "shirinliklar", "name": "Cheesecake", "emoji": "🍰", "description": "Klubnikali tort", "price": 42000, "weight": "150g"},
    {"category": "shirinliklar", "name": "Medovik", "emoji": "🍯", "description": "Asalli tort", "price": 38000, "badge": "hot", "weight": "150g"},
    {"category": "shirinliklar", "name": "Napoleon", "emoji": "🥐", "description": "Klassik napoleon", "price": 35000, "weight": "150g"},
    {"category": "shirinliklar", "name": "Browni", "emoji": "🍫", "description": "Shokoladli pirojnoe", "price": 28000, "weight": "120g"},
    {"category": "shirinliklar", "name": "Eklер", "emoji": "🥧", "description": "Kremli ekler", "price": 18000, "weight": "80g"},
    {"category": "shirinliklar", "name": "Donut Glazur", "emoji": "🍩", "description": "Glazurli donut", "price": 15000, "weight": "80g"},
    {"category": "shirinliklar", "name": "Donut Shokolad", "emoji": "🍩", "description": "Shokoladli donut", "price": 18000, "badge": "new", "weight": "90g"},
    {"category": "shirinliklar", "name": "Muzqaymoq Vanil", "emoji": "🍦", "description": "Vanilli muzqaymoq", "price": 15000, "weight": "150g"},
    {"category": "shirinliklar", "name": "Muzqaymoq Shokolad", "emoji": "🍦", "description": "Shokoladli muzqaymoq", "price": 18000, "weight": "150g"},
    {"category": "shirinliklar", "name": "Panna Cotta", "emoji": "🍮", "description": "Italyan shirinligi", "price": 32000, "badge": "new", "weight": "120g"},
    {"category": "shirinliklar", "name": "Muffin", "emoji": "🧁", "description": "Shokoladli muffin", "price": 12000, "weight": "80g"},
    {"category": "shirinliklar", "name": "Croissant", "emoji": "🥐", "description": "Frantsuz kruassani", "price": 18000, "weight": "100g"},
    {"category": "shirinliklar", "name": "Halvo", "emoji": "🍬", "description": "O'zbek halvosi", "price": 25000, "weight": "200g"},
    {"category": "shirinliklar", "name": "Baklava", "emoji": "🍯", "description": "Yong'oqli baklava", "price": 35000, "badge": "hot", "weight": "150g"},
]

created_count = 0
for p in PRODUCTS:
    cat = Category.objects.get(slug=p.pop("category"))
    obj, created = Product.objects.update_or_create(
        name=p["name"],
        defaults={**p, "category": cat, "stock": 15, "is_active": True, "is_featured": True},
    )
    if created:
        created_count += 1

print(f">>> Products: {Product.objects.count()} (yangi: {created_count})")
print(">>> SEED DONE.")
