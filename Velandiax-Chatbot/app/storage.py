from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any


class OrderRepository:
    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.Lock()

    def save(self, order: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(order, ensure_ascii=False)
        with self._lock, self.path.open("a", encoding="utf-8") as file:
            file.write(line + "\n")

