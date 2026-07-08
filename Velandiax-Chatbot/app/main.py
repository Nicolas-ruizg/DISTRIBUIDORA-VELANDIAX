from __future__ import annotations

import hashlib
import hmac
import logging
from collections import deque
from contextlib import asynccontextmanager
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, Request, Response

from app.backend import VelandiaxBackend
from app.bot import SalesBot
from app.catalog import Catalog, money
from app.config import Settings
from app.gemini import GeminiAssistant
from app.storage import OrderRepository
from app.whatsapp import WhatsAppClient, extract_text_messages


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = Settings()
catalog = Catalog.from_file(settings.products_file)
bot = SalesBot(
    catalog,
    OrderRepository(settings.orders_file),
    settings.store_url,
    settings.volume_min_quantity,
)
whatsapp = WhatsAppClient(settings)
backend = VelandiaxBackend(settings)
gemini = GeminiAssistant(settings, catalog)
processed_ids: set[str] = set()
processed_order: deque[str] = deque()

@asynccontextmanager
async def lifespan(_: FastAPI):
    if backend.configured:
        try:
            catalog.replace(await backend.fetch_catalog())
            logger.info("Catalogo cargado desde la API: %s variantes", len(catalog.products))
        except Exception:
            logger.exception("No fue posible cargar la API; se usara el catalogo local")
    yield


app = FastAPI(
    title="Velandiax WhatsApp Chatbot",
    version="0.2.0",
    lifespan=lifespan,
)


@app.get("/")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "velandiax-whatsapp-bot",
        "meta_configured": not settings.missing_meta_values(),
        "backend_configured": backend.configured,
        "backend_create_orders": settings.backend_create_orders,
        "backend_order_ready": bool(
            backend.configured
            and settings.backend_create_orders
            and settings.backend_email
            and settings.backend_password
        ),
        "gemini_configured": gemini.configured,
        "catalog_variants": len(catalog.products),
        "volume_min_quantity": settings.volume_min_quantity,
        "missing": settings.missing_meta_values(),
    }


@app.get("/webhook")
async def verify_webhook(
    mode: str | None = Query(None, alias="hub.mode"),
    token: str | None = Query(None, alias="hub.verify_token"),
    challenge: str | None = Query(None, alias="hub.challenge"),
) -> Response:
    if mode == "subscribe" and token and hmac.compare_digest(token, settings.verify_token):
        return Response(content=challenge or "", media_type="text/plain")
    raise HTTPException(status_code=403, detail="No fue posible verificar el webhook")


def valid_signature(body: bytes, signature: str | None) -> bool:
    if not settings.app_secret:
        logger.warning("META_APP_SECRET no configurado; se omite la validacion de firma")
        return True
    if not signature or not signature.startswith("sha256="):
        return False
    expected = hmac.new(settings.app_secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature.removeprefix("sha256="), expected)


@app.post("/webhook")
async def receive_webhook(request: Request, tasks: BackgroundTasks) -> dict[str, str]:
    body = await request.body()
    if not valid_signature(body, request.headers.get("x-hub-signature-256")):
        raise HTTPException(status_code=401, detail="Firma invalida")
    try:
        payload = await request.json()
    except ValueError as error:
        raise HTTPException(status_code=400, detail="JSON invalido") from error
    tasks.add_task(process_payload, payload)
    return {"status": "accepted"}


async def process_payload(payload: dict[str, Any]) -> None:
    for message in extract_text_messages(payload):
        message_id = message["id"]
        if message_id and message_id in processed_ids:
            continue
        if message_id:
            processed_ids.add(message_id)
            processed_order.append(message_id)
            if len(processed_order) > 2_000:
                processed_ids.discard(processed_order.popleft())
        try:
            if message_id:
                await whatsapp.mark_as_read(message_id)
            reply = bot.handle(message["from"], message["text"])
            if reply.action == "gemini":
                decision = await gemini.interpret(
                    message["text"],
                    bot.state_for_ai(message["from"]),
                    bot.cart_summary_for_ai(message["from"]),
                )
                reply = bot.handle_ai(message["from"], decision)
            if reply.action == "tracking":
                await whatsapp.send_text(message["from"], await tracking_text(message["from"]))
                await whatsapp.send_action(
                    message["from"],
                    bot._main_buttons("¿Qué más deseas hacer?"),
                )
                continue
            if reply.action == "human" and settings.admin_number:
                await whatsapp.send_text(
                    settings.admin_number,
                    f"🙋 El cliente {message['from']} solicita hablar con un asesor.",
                )
            if reply.order:
                if settings.backend_create_orders and backend.configured:
                    try:
                        remote_order = await backend.create_order(reply.order)
                        reply.order["backend_id"] = remote_order.get("id_pedido")
                        bot.finalize_order(message["from"], reply.order)
                        reply.messages = [
                            f"¡Pedido *#{reply.order['backend_id']}* confirmado! 🎉\n"
                            f"Total: *{money(reply.order['total'])}*\n"
                            "Un asesor coordinará contigo el pago y el despacho."
                        ]
                        reply.interactive = [bot._main_buttons("¿Necesitas algo más?")]
                    except Exception as error:
                        reply.order["backend_sync_error"] = type(error).__name__
                        logger.exception("El pedido %s no se sincronizo", reply.order["id"])
                        reply.messages = [
                            "No pude registrar el pedido en la base de datos. Tu carrito sigue "
                            "intacto; inténtalo nuevamente o solicita un asesor."
                        ]
                        reply.interactive = [bot._confirm_buttons()]
                else:
                    reply.messages = [
                        "El registro de pedidos en la base de datos aún no está configurado. "
                        "Tu carrito sigue intacto; solicita a Velandiax habilitar la cuenta de ventas."
                    ]
                    reply.interactive = [bot._confirm_buttons()]
            for text in reply.messages:
                await whatsapp.send_text(message["from"], text)
            for action in reply.interactive:
                await whatsapp.send_action(message["from"], action)
            if reply.order and settings.admin_number:
                await whatsapp.send_text(settings.admin_number, admin_order_text(reply.order))
        except Exception:
            logger.exception("Error procesando el mensaje %s", message_id)


def admin_order_text(order: dict[str, Any]) -> str:
    customer = order["customer"]
    items = "\n".join(
        f"• {item['quantity']} × {item['name']}" for item in order["items"]
    )
    backend_reference = (
        f"\nPedido en sistema: #{order['backend_id']}" if order.get("backend_id") else ""
    )
    return (
        f"🛍️ *Nuevo pedido {order['id']}*\n"
        f"Cliente: {customer['name']}\nWhatsApp: {order['phone']}\n"
        f"Ciudad: {customer['city']}\nDirección: {customer['address']}\n"
        f"{items}\n*Total: {money(order['total'])}*{backend_reference}"
    )


async def tracking_text(phone: str) -> str:
    if not backend.configured:
        return "El seguimiento aún no está conectado. Un asesor puede ayudarte con tu pedido."
    try:
        orders = await backend.tracking(phone)
    except Exception:
        logger.exception("No fue posible consultar seguimiento para %s", phone)
        return "No pude consultar el seguimiento en este momento. Inténtalo nuevamente más tarde."
    if not orders:
        return "No encontré pedidos activos asociados a este número de WhatsApp."
    lines = ["*Tus pedidos activos*"]
    for order in orders:
        status = order.get("estado_envio") or order.get("estado") or "PENDIENTE"
        guide = f" — guía {order['numero_guia']}" if order.get("numero_guia") else ""
        payment = order.get("estado_pago") or "SIN CONFIRMAR"
        lines.append(
            f"• Pedido #{order['id_pedido']}: *{status}*{guide}\n"
            f"  Pago: {payment} · Total: {money(int(order.get('total') or 0))}"
        )
    return "\n".join(lines)
