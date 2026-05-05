"""Tiny JSON-based persistence layer for demo API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


def _file_path(name: str) -> Path:
    return DATA_DIR / f"{name}.json"


def load_json(name: str, default: Any) -> Any:
    path = _file_path(name)
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def save_json(name: str, payload: Any) -> None:
    path = _file_path(name)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
