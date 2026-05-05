"""Large seed product catalog for frontend/backend sync."""

from __future__ import annotations


def _build(category: str, emoji: str, names: list[str], base_price: int) -> list[dict]:
    data: list[dict] = []
    for index, name in enumerate(names, start=1):
        data.append(
            {
                "cat": category,
                "emoji": emoji,
                "name": name,
                "desc": f"{name} uchun maxsus retsept",
                "price": base_price + index * 2000,
                "badge": "new" if index % 5 == 0 else ("hot" if index % 3 == 0 else ""),
                "image": "",
                "stock": 15,
            }
        )
    return data


FASTFOOD = _build(
    "fastfood",
    "🍔",
    [
        "Classic Burger",
        "Double Burger",
        "Cheese Burger",
        "BBQ Burger",
        "Hot Dog",
        "Doner Kebab",
        "Shawarma",
        "Lavash",
        "Taco",
        "Pizza Mini",
        "Pizza Grande",
        "Nuggets",
        "French Fries",
        "Onion Rings",
        "Combo Fast",
        "Grill Sandwich",
    ],
    18000,
)

DRINKS = _build(
    "drinks",
    "🥤",
    [
        "Coca Cola",
        "Pepsi",
        "Fanta",
        "Sprite",
        "Americano",
        "Cappuccino",
        "Latte",
        "Mocha",
        "Milkshake Vanilla",
        "Milkshake Chocolate",
        "Bubble Tea",
        "Fresh Orange",
        "Fresh Apple",
        "Green Tea",
        "Black Tea",
        "Lemonade",
    ],
    9000,
)

MILLIY = _build(
    "milliy",
    "🍲",
    [
        "Toshkent Palov",
        "Samarqand Palov",
        "Manti",
        "Chuchvara",
        "Lagmon",
        "Shurva",
        "Mastava",
        "Qozon Kabob",
        "Jiz Biz",
        "Qovurma",
        "Norin",
        "Hasip",
        "Dimlama",
        "Tandir Gosht",
        "Somsa",
        "Shivit Oshi",
    ],
    22000,
)

SWEETS = _build(
    "sweets",
    "🍰",
    [
        "Napoleon Cake",
        "Honey Cake",
        "Cheesecake",
        "Brownie",
        "Eclair",
        "Donut",
        "Croissant",
        "Cupcake",
        "Chocolate Roll",
        "Tiramisu",
        "Panna Cotta",
        "Ice Cream",
        "Baklava",
        "Chak Chak",
        "Halva",
        "Qandolat Mix",
    ],
    14000,
)


PRODUCTS: list[dict] = []
for counter, item in enumerate(FASTFOOD + DRINKS + MILLIY + SWEETS, start=1):
    row = dict(item)
    row["id"] = counter
    PRODUCTS.append(row)
