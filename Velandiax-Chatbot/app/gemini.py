from __future__ import annotations

import json
import logging
from dataclasses import dataclass

import httpx

from app.catalog import Catalog
from app.config import Settings


logger = logging.getLogger(__name__)

INTENTS = (
    "menu",
    "catalog",
    "offers",
    "package",
    "recommend",
    "product_search",
    "add_product",
    "cart",
    "favorites",
    "checkout",
    "tracking",
    "business_info",
    "human",
    "unknown",
)


@dataclass(slots=True)
class IntentDecision:
    intent: str
    query: str = ""
    product_reference: str = ""
    quantity: int = 1
    reply: str = ""


class GeminiAssistant:
    """Interpreta lenguaje natural; las acciones se ejecutan fuera del modelo."""

    def __init__(self, settings: Settings, catalog: Catalog):
        self.settings = settings
        self.catalog = catalog

    @property
    def configured(self) -> bool:
        return bool(self.settings.gemini_api_key)

    async def interpret(self, message: str, state: str, cart_summary: str) -> IntentDecision:
        if not self.configured:
            return self._fallback(message)

        products = "\n".join(
            f"- {product.sku}: {product.name}; categoría={product.category}; "
            f"precio={product.price}; atributos={dict(product.attributes)}"
            for product in self.catalog.products[:80]
        )
        prompt = (
            f"Mensaje del cliente: {message!r}\n"
            f"Estado de conversación: {state}\n"
            f"Carrito: {cart_summary}\n\n"
            f"Catálogo real:\n{products}"
        )
        schema = {
            "type": "OBJECT",
            "properties": {
                "intent": {"type": "STRING", "enum": list(INTENTS)},
                "query": {"type": "STRING"},
                "product_reference": {"type": "STRING"},
                "quantity": {"type": "INTEGER", "minimum": 1, "maximum": 999},
                "reply": {"type": "STRING"},
            },
            "required": ["intent", "query", "product_reference", "quantity", "reply"],
        }
        payload = {
            "systemInstruction": {
                "parts": [{"text": self._system_prompt()}],
            },
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
                "responseSchema": schema,
            },
        }
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.settings.gemini_model}:generateContent"
        )
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(
                    url,
                    headers={"x-goog-api-key": self.settings.gemini_api_key},
                    json=payload,
                )
                response.raise_for_status()
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            data = json.loads(text)
            return IntentDecision(
                intent=data.get("intent", "unknown"),
                query=str(data.get("query", "")),
                product_reference=str(data.get("product_reference", "")),
                quantity=max(1, min(int(data.get("quantity", 1)), 999)),
                reply=str(data.get("reply", ""))[:700],
            )
        except Exception:
            logger.exception("Gemini no pudo interpretar el mensaje")
            return self._fallback(message)

    def _system_prompt(self) -> str:
        return (
            "Eres el intérprete comercial de Velandiax, una tienda de ropa en Colombia. "
            "Clasifica la intención del cliente usando exclusivamente el catálogo entregado. "
            f"Reglas: desde {self.settings.volume_min_quantity} unidades el sistema aplica internamente "
            "el precio especial por volumen a todo el carrito. Nunca reveles ni menciones el precio "
            "mayorista unitario. La compra por volumen solo usa variantes habilitadas para paca. "
            "Nunca inventes productos, precios, descuentos, stock, estados de pedidos ni políticas. "
            "Nunca confirmes una compra: checkout y confirmación los controla el sistema. "
            "Si pide un producto por características, usa product_search o recommend y coloca esas "
            "características en query. product_reference solo debe contener un SKU exacto cuando sea "
            "inequívoco. Responde en español colombiano, breve, amable y sin Markdown complejo."
        )

    @staticmethod
    def _fallback(message: str) -> IntentDecision:
        normalized = message.lower()
        if any(word in normalized for word in ("pedido", "envío", "envio", "guía", "guia", "rastre")):
            return IntentDecision("tracking")
        if any(word in normalized for word in ("oferta", "descuento", "sale")):
            return IntentDecision("offers")
        if any(word in normalized for word in ("paca", "mayorista", "por mayor")):
            return IntentDecision("package")
        if any(word in normalized for word in ("carrito", "canasta")):
            return IntentDecision("cart")
        if any(word in normalized for word in ("favorito", "guardado", "me gusta")):
            return IntentDecision("favorites")
        if any(word in normalized for word in ("comprar", "pagar", "finalizar")):
            return IntentDecision("checkout")
        return IntentDecision("product_search", query=message)
