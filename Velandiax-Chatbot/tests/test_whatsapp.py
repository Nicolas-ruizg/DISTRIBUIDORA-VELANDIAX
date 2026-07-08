from pathlib import Path

import pytest

from app.config import Settings
from app.whatsapp import WhatsAppClient


@pytest.mark.anyio
async def test_interactive_payloads_respect_whatsapp_limits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = WhatsAppClient(Settings())
    payloads: list[dict] = []

    async def capture(payload: dict) -> None:
        payloads.append(payload)

    monkeypatch.setattr(client, "_send", capture)
    await client.send_buttons(
        "57",
        "Elige",
        [{"id": f"id-{index}", "title": "x" * 30} for index in range(5)],
    )
    await client.send_list(
        "57",
        "Productos",
        "Elige",
        "Ver",
        [{"title": "Sección", "rows": [
            {"id": str(index), "title": "p" * 30, "description": "d" * 90}
            for index in range(12)
        ]}],
    )

    buttons = payloads[0]["interactive"]["action"]["buttons"]
    rows = payloads[1]["interactive"]["action"]["sections"][0]["rows"]
    assert len(buttons) == 3
    assert all(len(button["reply"]["title"]) <= 20 for button in buttons)
    assert len(rows) == 10
    assert all(len(row["title"]) <= 24 for row in rows)
