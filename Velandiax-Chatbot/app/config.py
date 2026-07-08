from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(override=True, encoding="utf-8-sig")


@dataclass(frozen=True, slots=True)
class Settings:
    whatsapp_token: str = os.getenv("WHATSAPP_TOKEN", "")
    phone_number_id: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    verify_token: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
    app_secret: str = os.getenv("META_APP_SECRET", "")
    api_version: str = os.getenv("GRAPH_API_VERSION", "v25.0")
    admin_number: str = os.getenv("ADMIN_WHATSAPP_NUMBER", "")
    products_file: Path = Path(os.getenv("PRODUCTS_FILE", "data/products.json"))
    orders_file: Path = Path(os.getenv("ORDERS_FILE", "data/orders.jsonl"))
    backend_api_url: str = os.getenv("BACKEND_API_URL", "").rstrip("/")
    backend_email: str = os.getenv("BACKEND_API_EMAIL", "")
    backend_password: str = os.getenv("BACKEND_API_PASSWORD", "")
    backend_create_orders: bool = os.getenv("BACKEND_CREATE_ORDERS", "false").lower() in {
        "1", "true", "yes", "si"
    }
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    store_url: str = os.getenv("STORE_URL", "https://velandiax.com.co")
    volume_min_quantity: int = max(
        1,
        int(os.getenv("VOLUME_MIN_QUANTITY", "50")),
    )

    def missing_meta_values(self) -> list[str]:
        values = {
            "WHATSAPP_TOKEN": self.whatsapp_token,
            "WHATSAPP_PHONE_NUMBER_ID": self.phone_number_id,
            "WHATSAPP_VERIFY_TOKEN": self.verify_token,
        }
        return [name for name, value in values.items() if not value]
