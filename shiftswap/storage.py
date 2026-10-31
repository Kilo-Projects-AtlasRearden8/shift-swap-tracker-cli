"""Local JSON storage for the shift swap tracker."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from .models import Store


DEFAULT_DATA_FILE = "shifts.json"


def load_store(path: Union[str, Path] = DEFAULT_DATA_FILE) -> Store:
    """Load the store from a JSON file. Returns an empty store if missing/invalid."""
    p = Path(path)
    if not p.exists():
        return Store()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return Store()
    if not isinstance(data, dict):
        return Store()
    return Store.from_dict(data)


def save_store(store: Store, path: Union[str, Path] = DEFAULT_DATA_FILE) -> None:
    """Write the store to a JSON file, creating parent directories as needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(store.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")


def ensure_store(path: Union[str, Path] = DEFAULT_DATA_FILE) -> Store:
    """Ensure a store file exists, creating an empty one if needed."""
    p = Path(path)
    if not p.exists():
        save_store(Store(), p)
        return Store()
    return load_store(p)