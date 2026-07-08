from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import Settings


logger = logging.getLogger(__name__)


class WhatsAppClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.url = (
            f"https://graph.facebook.com/{settings.api_version}/"
            f"{settings.phone_number_id}/messages"
        )

    async def send_text(self, recipient: str, text: str) -> None:
        if not self.settings.whatsapp_token or not self.settings.phone_number_id:
            logger.warning("Mensaje no enviado: faltan credenciales de WhatsApp")
            return
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text[:4096]},
        }
        await self._send(payload)

    async def send_action(self, recipient: str, action: dict[str, Any]) -> None:
        action_type = action.get("type")
        if action_type == "buttons":
            await self.send_buttons(
                recipient,
                action["body"],
                action.get("buttons", []),
                action.get("footer"),
            )
        elif action_type == "list":
            await self.send_list(
                recipient,
                action.get("title", "Velandiax"),
                action["body"],
                action["button"],
                action.get("sections", []),
            )
        elif action_type == "image":
            await self.send_image(recipient, action["url"], action.get("caption", ""))

    async def send_buttons(
        self,
        recipient: str,
        body: str,
        buttons: list[dict[str, str]],
        footer: str | None = None,
    ) -> None:
        interactive: dict[str, Any] = {
            "type": "button",
            "body": {"text": body[:1024]},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {"id": item["id"][:256], "title": item["title"][:20]},
                    }
                    for item in buttons[:3]
                ]
            },
        }
        if footer:
            interactive["footer"] = {"text": footer[:60]}
        await self._send({
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "interactive",
            "interactive": interactive,
        })

    async def send_list(
        self,
        recipient: str,
        title: str,
        body: str,
        button: str,
        sections: list[dict[str, Any]],
    ) -> None:
        safe_sections = []
        remaining = 10
        for section in sections:
            rows = []
            for row in section.get("rows", []):
                if remaining <= 0:
                    break
                rows.append({
                    "id": row["id"][:200],
                    "title": row["title"][:24],
                    "description": row.get("description", "")[:72],
                })
                remaining -= 1
            if rows:
                safe_sections.append({"title": section.get("title", title)[:24], "rows": rows})
        await self._send({
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": title[:60]},
                "body": {"text": body[:1024]},
                "action": {"button": button[:20], "sections": safe_sections},
            },
        })

    async def send_image(self, recipient: str, url: str, caption: str = "") -> None:
        await self._send({
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "image",
            "image": {"link": url, "caption": caption[:1024]},
        })

    async def _send(self, payload: dict[str, Any]) -> None:
        if not self.settings.whatsapp_token or not self.settings.phone_number_id:
            logger.warning("Mensaje no enviado: faltan credenciales de WhatsApp")
            return
        headers = {
            "Authorization": f"Bearer {self.settings.whatsapp_token}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(self.url, headers=headers, json=payload)
            if response.is_error:
                logger.error("WhatsApp rechazo el mensaje: %s", response.text)
            response.raise_for_status()

    async def mark_as_read(self, message_id: str) -> None:
        if not self.settings.whatsapp_token or not self.settings.phone_number_id:
            return
        headers = {
            "Authorization": f"Bearer {self.settings.whatsapp_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(self.url, headers=headers, json=payload)
            if response.is_error:
                logger.warning("WhatsApp no permitio marcar como leido: %s", response.text)
                return


def extract_text_messages(payload: dict[str, Any]) -> list[dict[str, str]]:
    extracted: list[dict[str, str]] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for message in value.get("messages", []):
                text = ""
                if message.get("type") == "text":
                    text = message.get("text", {}).get("body", "")
                elif message.get("type") == "interactive":
                    interactive = message.get("interactive", {})
                    selection = interactive.get("button_reply") or interactive.get("list_reply") or {}
                    text = selection.get("id", "")
                if text:
                    extracted.append(
                        {"id": message.get("id", ""), "from": message.get("from", ""), "text": text}
                    )
    return extracted
