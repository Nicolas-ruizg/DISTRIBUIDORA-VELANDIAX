from typing import Any

import pytest

from app.main import admin_order_text, backend, tracking_text


def test_admin_order_notification() -> None:
    text = admin_order_text(
        {
            "id": "VEL-ABC",
            "backend_id": 42,
            "phone": "573001234567",
            "customer": {"name": "Ada", "city": "Bogotá", "address": "Calle 1"},
            "items": [{"quantity": 2, "name": "Producto"}],
            "total": 20000,
        }
    )
    assert "VEL-ABC" in text
    assert "#42" in text
    assert "$20.000" in text


@pytest.mark.anyio
async def test_tracking_text(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(type(backend), "configured", property(lambda _: True))

    async def fake_tracking(_: str) -> list[dict[str, Any]]:
        return [{"id_pedido": 7, "estado": "PENDIENTE", "numero_guia": None}]

    monkeypatch.setattr(backend, "tracking", fake_tracking)
    text = await tracking_text("573001234567")
    assert "Pedido #7" in text
    assert "PENDIENTE" in text
