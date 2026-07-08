from __future__ import annotations

import re
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.catalog import Catalog, Product, money, normalize
from app.gemini import IntentDecision
from app.storage import OrderRepository


@dataclass(slots=True)
class Session:
    state: str = "menu"
    cart: dict[str, int] = field(default_factory=dict)
    customer: dict[str, str] = field(default_factory=dict)
    package_mode: bool = False
    favorites: set[str] = field(default_factory=set)
    pending_sku: str = ""
    quantity_mode: str = "add"


@dataclass(slots=True)
class BotReply:
    messages: list[str] = field(default_factory=list)
    interactive: list[dict[str, Any]] = field(default_factory=list)
    order: dict[str, Any] | None = None
    action: str | None = None


class SalesBot:
    PAGE_SIZE = 7

    def __init__(
        self,
        catalog: Catalog,
        orders: OrderRepository,
        store_url: str = "",
        volume_min_quantity: int = 50,
    ):
        self.catalog = catalog
        self.orders = orders
        self.store_url = store_url
        self.volume_min_quantity = max(1, volume_min_quantity)
        self.sessions: dict[str, Session] = {}

    def handle(self, phone: str, incoming: str) -> BotReply:
        session = self.sessions.setdefault(phone, Session())
        text = incoming.strip()
        command = normalize(text)

        if text.startswith(("menu:", "catalog:", "category:", "product:", "add:", "quantity:", "quantityedit:", "qty:", "cart:", "remove:", "favorite:", "favorites:", "checkout:", "order:")):
            return self._handle_interactive(phone, session, text)
        if text == "tracking":
            return BotReply(action="tracking")

        if command in {"cancelar", "salir"}:
            session.state = "menu"
            session.customer.clear()
            return self._welcome("Operación cancelada.")

        if session.state == "quantity_input":
            if not command.isdigit() or not 1 <= int(command) <= 999:
                return BotReply(["Escribe una cantidad entre 1 y 999, solo con números."])
            quantity = int(command)
            sku = session.pending_sku
            mode = session.quantity_mode
            session.state = "menu"
            session.pending_sku = ""
            return (
                self._set_product_quantity(session, sku, quantity)
                if mode == "set"
                else self._add_product(session, sku, quantity)
            )

        if session.state == "checkout_name":
            session.customer["name"] = text
            session.state = "checkout_document"
            return BotReply(["¿Cuál es tu número de cédula o NIT?"])
        if session.state == "checkout_document":
            session.customer["document"] = text
            session.state = "checkout_city"
            return BotReply(["¿En qué ciudad te encuentras?"])
        if session.state == "checkout_city":
            session.customer["city"] = text
            session.state = "checkout_address"
            return BotReply(["¿Cuál es la dirección de entrega?"])
        if session.state == "checkout_address":
            session.customer["address"] = text
            session.state = "checkout_notes"
            return BotReply(["¿Tienes alguna indicación para la entrega? Escribe *NO* para omitirla."])
        if session.state == "checkout_notes":
            session.customer["notes"] = "" if command in {"no", "ninguna", "omitir"} else text
            session.state = "checkout_confirm"
            return self._confirmation(session)
        if session.state == "checkout_confirm":
            if command in {"si", "confirmar", "confirmo"}:
                return self._complete_order(phone, session)
            return BotReply(
                ["Para proteger tu compra, confirma usando uno de los botones."],
                [self._confirm_buttons()],
            )
        if session.state == "advising":
            return BotReply(action="gemini")

        if command in {"hola", "buenas", "inicio", "menu", "ayuda", "buenos dias", "buenas tardes"}:
            return self._welcome()
        if command in {"catalogo", "productos", "comprar", "tienda"}:
            return self._shop_menu()
        if command in {"ofertas", "descuentos", "sale"}:
            return self._catalog_reply("offers", 0)
        if command in {"paca", "mayorista", "por mayor"}:
            session.package_mode = True
            return self._catalog_reply("package", 0)
        if command in {"carrito", "canasta"}:
            return self._cart_reply(session)
        if command in {"finalizar", "checkout", "hacer pedido"}:
            return self._start_checkout(session)
        if command in {"seguimiento", "rastrear", "mis pedidos", "mi pedido"}:
            return BotReply(action="tracking")
        if command in {"asesoria", "asesor", "recomiendame"}:
            session.state = "advising"
            return BotReply(["Cuéntame con tus palabras qué prenda buscas, talla, color y presupuesto."])

        add_match = re.fullmatch(r"(?:agregar|anadir|añadir)\s+(?:(\d+)\s+)?(.+)", command)
        if add_match:
            quantity = int(add_match.group(1) or 1)
            return self._add_product(session, add_match.group(2), quantity)
        return BotReply(action="gemini")

    def handle_ai(self, phone: str, decision: IntentDecision) -> BotReply:
        session = self.sessions.setdefault(phone, Session())
        intent = decision.intent
        if intent == "menu":
            return self._welcome(decision.reply)
        if intent == "catalog":
            return self._shop_menu(decision.reply)
        if intent == "offers":
            session.package_mode = False
            return self._catalog_reply("offers", 0, decision.reply)
        if intent == "package":
            session.package_mode = True
            return self._catalog_reply("package", 0, decision.reply)
        if intent in {"recommend", "product_search"}:
            session.state = "menu"
            session.package_mode = False
            query = decision.query or decision.reply
            return self._search_reply(query, decision.reply)
        if intent == "add_product":
            product = self.catalog.find(decision.product_reference)
            if product:
                return self._add_product(session, product.sku, decision.quantity)
            return self._search_reply(decision.query or decision.product_reference, decision.reply)
        if intent == "cart":
            return self._cart_reply(session)
        if intent == "favorites":
            return self._favorites_reply(session)
        if intent == "checkout":
            return self._start_checkout(session)
        if intent == "tracking":
            return BotReply(action="tracking")
        if intent == "business_info":
            message = decision.reply or "Puedes comprar aquí mismo conmigo."
            if self.store_url:
                message += f"\n\nTambién puedes visitar {self.store_url}"
            return self._welcome(message)
        if intent == "human":
            return BotReply(
                ["Le avisaré a un asesor para que continúe contigo. Mientras tanto puedes explorar la tienda."],
                [self._main_buttons()],
                action="human",
            )
        return self._welcome(decision.reply or "No alcancé a entenderte del todo. Elige una opción:")

    def cart_summary_for_ai(self, phone: str) -> str:
        session = self.sessions.setdefault(phone, Session())
        if not session.cart:
            return "vacío"
        return ", ".join(f"{quantity}x {sku}" for sku, quantity in session.cart.items())

    def state_for_ai(self, phone: str) -> str:
        return self.sessions.setdefault(phone, Session()).state

    def _handle_interactive(self, phone: str, session: Session, value: str) -> BotReply:
        if value == "menu:main":
            return self._welcome()
        if value == "menu:shop":
            return self._shop_menu()
        if value == "menu:advice":
            session.state = "advising"
            return BotReply(["Cuéntame qué buscas. Por ejemplo: “quiero una camiseta negra talla M”."])
        if value.startswith("menu:categories"):
            session.package_mode = False
            parts = value.split(":")
            return self._categories_reply(int(parts[2]) if len(parts) > 2 else 0)
        if value.startswith("category:"):
            _, category_id, page = value.split(":", 2)
            session.package_mode = False
            return self._catalog_reply(f"category-{category_id}", int(page))
        if value.startswith("catalog:"):
            _, source, page = value.split(":", 2)
            session.package_mode = source == "package"
            return self._catalog_reply(source, int(page))
        if value.startswith("product:"):
            return self._product_reply(value.removeprefix("product:"))
        if value.startswith("quantityedit:"):
            return self._quantity_menu(value.removeprefix("quantityedit:"), "set")
        if value.startswith("quantity:"):
            return self._quantity_menu(value.removeprefix("quantity:"), "add")
        if value.startswith("qty:"):
            parts = value.split(":")
            if len(parts) == 4 and parts[1] in {"add", "set"}:
                mode, sku, raw_quantity = parts[1], parts[2], parts[3]
                if raw_quantity == "custom":
                    session.state = "quantity_input"
                    session.pending_sku = sku
                    session.quantity_mode = mode
                    product = self.catalog.find(sku)
                    name = product.name if product else "el producto"
                    return BotReply([f"¿Cuántas unidades de *{name}* deseas? Escribe un número del 1 al 999."])
                quantity = int(raw_quantity)
                return (
                    self._set_product_quantity(session, sku, quantity)
                    if mode == "set"
                    else self._add_product(session, sku, quantity)
                )
        if value.startswith("add:"):
            return self._add_product(session, value.removeprefix("add:"))
        if value == "cart:view":
            return self._cart_reply(session)
        if value in {"cart:remove", "cart:edit"}:
            return self._edit_cart_menu(session)
        if value == "favorites:view":
            return self._favorites_reply(session)
        if value.startswith("favorite:"):
            return self._toggle_favorite(session, value.removeprefix("favorite:"))
        if value.startswith("remove:"):
            return self._remove_product(session, value.removeprefix("remove:"))
        if value == "checkout:start":
            return self._start_checkout(session)
        if value == "checkout:cancel" or value == "order:cancel":
            session.state = "menu"
            session.customer.clear()
            return self._cart_reply(session, "Compra cancelada; tu carrito sigue guardado.")
        if value == "order:confirm":
            if session.state != "checkout_confirm":
                return self._cart_reply(session)
            return self._complete_order(phone, session)
        return self._welcome()

    def _welcome(self, prefix: str = "") -> BotReply:
        body = "Soy el asistente de *Velandiax*. ¿Qué quieres hacer?"
        if prefix:
            body = f"{prefix}\n\n{body}"
        return BotReply(interactive=[self._main_buttons(body)])

    @staticmethod
    def _main_buttons(body: str = "Soy el asistente de *Velandiax*. ¿Qué quieres hacer?") -> dict[str, Any]:
        return {
            "type": "buttons",
            "body": body,
            "footer": "Compra fácil por WhatsApp",
            "buttons": [
                {"id": "menu:shop", "title": "🛍️ Comprar"},
                {"id": "tracking", "title": "📦 Mi pedido"},
                {"id": "menu:advice", "title": "💬 Asesoría"},
            ],
        }

    def _shop_menu(self, prefix: str = "") -> BotReply:
        body = prefix or "Explora nuestra tienda y elige cómo quieres comprar."
        rows = [
            {"id": "menu:categories", "title": "Por categorías", "description": "Busca el tipo de prenda"},
            {"id": "catalog:all:0", "title": "Todos los productos", "description": "Catálogo completo"},
            {"id": "catalog:offers:0", "title": "Ofertas", "description": "Productos con descuento"},
            {
                "id": "catalog:package:0",
                "title": "Compra por volumen",
                "description": f"Desde {self.volume_min_quantity} unidades con precio especial",
            },
            {"id": "favorites:view", "title": "Mis favoritos", "description": "Productos que guardaste"},
            {"id": "cart:view", "title": "Ver carrito", "description": "Revisa tu compra"},
        ]
        return BotReply(interactive=[self._list("Tienda Velandiax", body, "Ver tienda", rows)])

    def _categories_reply(self, page: int) -> BotReply:
        categories = self.catalog.categories()
        start = page * 8
        rows = [
            {
                "id": f"category:{category_id}:0",
                "title": self._short(name, 24),
                "description": "Ver productos de esta categoría",
            }
            for category_id, name in categories[start : start + 8]
        ]
        if page > 0:
            rows.append({"id": f"menu:categories:{page - 1}", "title": "← Anteriores", "description": "Volver"})
        if start + 8 < len(categories):
            rows.append({"id": f"menu:categories:{page + 1}", "title": "Más categorías →", "description": "Continuar"})
        return BotReply(interactive=[self._list("Categorías", "¿Qué tipo de producto buscas?", "Elegir", rows)])

    def _products_for_source(self, source: str) -> list[Product]:
        if source == "offers":
            return [product for product in self.catalog.products if product.on_sale]
        if source == "package":
            return [product for product in self.catalog.products if product.package_eligible]
        if source.startswith("category-"):
            category_id = int(source.removeprefix("category-"))
            return [product for product in self.catalog.products if product.category_id == category_id]
        return self.catalog.products

    def _catalog_reply(self, source: str, page: int, prefix: str = "") -> BotReply:
        products = self._products_for_source(source)
        if not products:
            return self._shop_menu("No hay productos disponibles en esa sección por ahora.")
        start = page * self.PAGE_SIZE
        page_products = products[start : start + self.PAGE_SIZE]
        rows = [self._product_row(product) for product in page_products]
        if page > 0:
            rows.append({"id": f"catalog:{source}:{page - 1}", "title": "← Anteriores", "description": "Página anterior"})
        if start + self.PAGE_SIZE < len(products):
            rows.append({"id": f"catalog:{source}:{page + 1}", "title": "Más productos →", "description": "Página siguiente"})
        body = prefix or (
            "Elige prendas para tu compra por volumen."
            if source == "package"
            else "Selecciona un producto para ver fotos y detalles."
        )
        return BotReply(interactive=[self._list("Productos", body, "Ver productos", rows)])

    def _search_reply(self, query: str, prefix: str = "") -> BotReply:
        products = self.catalog.search(query)
        if not products:
            return self._shop_menu(prefix or "No encontré una coincidencia exacta. Puedes explorar la tienda:")
        rows = [self._product_row(product) for product in products[:10]]
        body = prefix or f"Encontré estas opciones para “{self._short(query, 80)}”."
        return BotReply(interactive=[self._list("Recomendaciones", body, "Ver opciones", rows)])

    def _product_row(self, product: Product) -> dict[str, str]:
        price = money(product.price)
        attributes = " · ".join(value for _, value in product.attributes)
        description = f"{price} · {attributes}" if attributes else f"{price} · {product.category}"
        return {
            "id": f"product:{product.sku}",
            "title": self._short(product.name, 24),
            "description": self._short(description, 72),
        }

    def _product_reply(self, reference: str) -> BotReply:
        product = self.catalog.find(reference)
        if not product:
            return self._shop_menu("Ese producto ya no está disponible.")
        attributes = "\n".join(f"• {key}: {value}" for key, value in product.attributes)
        price_lines = [f"Precio: *{money(product.price)}*"]
        if product.on_sale and product.previous_price:
            price_lines.insert(0, f"Antes: ~{money(product.previous_price)}~")
        caption = (
            f"*{product.name}*\n{product.description}\n\n"
            f"{'\n'.join(price_lines)}"
            + (f"\n\n{attributes}" if attributes else "")
        )
        actions: list[dict[str, Any]] = []
        if product.image_url:
            actions.append({"type": "image", "url": product.image_url, "caption": caption})
            button_body = f"¿Quieres agregar {self._short(product.name, 80)}?"
        else:
            button_body = caption
        actions.append(
            {
                "type": "buttons",
                "body": button_body,
                "buttons": [
                    {"id": f"quantity:{product.sku}", "title": "Elegir cantidad"},
                    {"id": f"favorite:{product.sku}", "title": "Favorito"},
                    {"id": "cart:view", "title": "Ver carrito"},
                ],
            }
        )
        return BotReply(interactive=actions)

    def _toggle_favorite(self, session: Session, reference: str) -> BotReply:
        product = self.catalog.find(reference)
        if not product:
            return self._shop_menu("Ese producto ya no está disponible.")
        if product.sku in session.favorites:
            session.favorites.remove(product.sku)
            message = f"Quité *{product.name}* de favoritos."
        else:
            session.favorites.add(product.sku)
            message = f"Guardé *{product.name}* en favoritos ❤️"
        return BotReply(
            [message],
            [{"type": "buttons", "body": "¿Qué deseas hacer?", "buttons": [
                {"id": f"quantity:{product.sku}", "title": "Elegir cantidad"},
                {"id": "favorites:view", "title": "Ver favoritos"},
                {"id": "menu:shop", "title": "Seguir viendo"},
            ]}],
        )

    def _favorites_reply(self, session: Session) -> BotReply:
        products = [
            self.catalog.by_sku[sku]
            for sku in session.favorites
            if sku in self.catalog.by_sku
        ]
        if not products:
            return self._shop_menu("Aún no has guardado favoritos. Abre un producto y pulsa *Favorito*.")
        return BotReply(
            interactive=[self._list(
                "Mis favoritos",
                "Selecciona un producto guardado.",
                "Ver favoritos",
                [self._product_row(product) for product in products[:10]],
            )]
        )

    def _add_product(self, session: Session, reference: str, quantity: int = 1) -> BotReply:
        product = self.catalog.find(reference)
        if not product:
            matches = self.catalog.search(reference, 8)
            if matches:
                return BotReply(interactive=[self._list("¿Cuál producto?", "Elige una opción:", "Ver", [self._product_row(item) for item in matches])])
            return self._shop_menu("No encontré ese producto.")
        if session.package_mode and not product.package_eligible:
            return self._catalog_reply("package", 0, "Esa variante no está habilitada para paca.")
        cart_deposits = {
            self.catalog.by_sku[sku].deposit_id
            for sku in session.cart
            if self.catalog.by_sku[sku].deposit_id
        }
        if product.deposit_id and cart_deposits and product.deposit_id not in cart_deposits:
            return self._cart_reply(session, "Ese producto sale de otro depósito; debes finalizar este pedido primero.")
        quantity = max(1, min(quantity, 999))
        session.cart[product.sku] = session.cart.get(product.sku, 0) + quantity
        return self._cart_reply(session, f"Agregué {quantity} × *{product.name}* ✅")

    def _quantity_menu(self, reference: str, mode: str) -> BotReply:
        product = self.catalog.find(reference)
        if not product:
            return self._shop_menu("Ese producto ya no está disponible.")
        verb = "Dejar en" if mode == "set" else "Agregar"
        rows = [
            {
                "id": f"qty:{mode}:{product.sku}:{quantity}",
                "title": f"{quantity} unidad{'es' if quantity != 1 else ''}",
                "description": f"{verb} {quantity} unidad{'es' if quantity != 1 else ''}",
            }
            for quantity in (1, 5, 10, 25, 50, 100)
        ]
        if mode == "set":
            rows.append({
                "id": f"qty:set:{product.sku}:0",
                "title": "Quitar del carrito",
                "description": "Eliminar todas las unidades",
            })
        rows.append({
            "id": f"qty:{mode}:{product.sku}:custom",
            "title": "Otra cantidad",
            "description": "Escribir un número exacto",
        })
        return BotReply(interactive=[self._list(
            "Elegir cantidad",
            f"¿Cuántas unidades de {self._short(product.name, 80)} deseas?",
            "Seleccionar",
            rows,
        )])

    def _set_product_quantity(self, session: Session, reference: str, quantity: int) -> BotReply:
        product = self.catalog.find(reference)
        if not product or product.sku not in session.cart:
            return self._cart_reply(session, "Ese producto ya no está en tu carrito.")
        if quantity <= 0:
            session.cart.pop(product.sku, None)
            return self._cart_reply(session, f"Quité *{product.name}* del carrito.")
        session.cart[product.sku] = min(quantity, 999)
        return self._cart_reply(
            session,
            f"Actualicé *{product.name}* a {session.cart[product.sku]} unidades.",
        )

    def _remove_product(self, session: Session, reference: str) -> BotReply:
        product = self.catalog.find(reference)
        if not product or product.sku not in session.cart:
            return self._cart_reply(session, "Ese producto ya no estaba en tu carrito.")
        session.cart.pop(product.sku)
        return self._cart_reply(session, f"Quité *{product.name}* del carrito.")

    def _edit_cart_menu(self, session: Session) -> BotReply:
        if not session.cart:
            return self._cart_reply(session)
        rows = [
            {
                "id": f"quantityedit:{sku}",
                "title": self._short(self.catalog.by_sku[sku].name, 24),
                "description": f"Cantidad actual: {quantity}",
            }
            for sku, quantity in list(session.cart.items())[:10]
        ]
        return BotReply(interactive=[self._list(
            "Editar cantidades",
            "Selecciona la prenda que deseas modificar.",
            "Editar",
            rows,
        )])

    def _cart_reply(self, session: Session, prefix: str = "") -> BotReply:
        text = self._cart_text(session)
        if prefix:
            text = f"{prefix}\n\n{text}"
        if not session.cart:
            return BotReply(
                [text],
                [{"type": "buttons", "body": "¿Quieres explorar la tienda?", "buttons": [
                    {"id": "menu:shop", "title": "Ver productos"},
                    {"id": "menu:advice", "title": "Pedir asesoría"},
                ]}],
            )
        return BotReply(
            [text],
            [{
                "type": "buttons",
                "body": "¿Qué deseas hacer con tu carrito?",
                "buttons": [
                    {"id": "checkout:start", "title": "Finalizar compra"},
                    {"id": "cart:edit", "title": "Editar cantidades"},
                    {"id": "menu:shop", "title": "Seguir comprando"},
                ],
            }],
        )

    def _cart_text(self, session: Session) -> str:
        if not session.cart:
            return "Tu carrito está vacío."
        total_items = sum(session.cart.values())
        volume_price = total_items >= self.volume_min_quantity
        lines = [
            f"*Tu carrito · {total_items} unidades*",
            "Precio especial por volumen aplicado ✅"
            if volume_price
            else (
                f"Te faltan {self.volume_min_quantity - total_items} unidades para acceder "
                "al precio especial por volumen."
            ),
        ]
        total = 0
        for sku, quantity in session.cart.items():
            product = self.catalog.by_sku[sku]
            unit_price = self._unit_price(product, volume_price)
            subtotal = unit_price * quantity
            total += subtotal
            lines.append(f"• {quantity} × {product.name}: {money(subtotal)}")
        lines.append(f"\n*Total: {money(total)}*")
        return "\n".join(lines)

    @staticmethod
    def _unit_price(product: Product, volume_price: bool) -> int:
        if volume_price and product.wholesale_price is not None:
            return product.wholesale_price
        return product.price

    def _start_checkout(self, session: Session) -> BotReply:
        if not session.cart:
            return self._cart_reply(session, "Primero agrega productos.")
        session.state = "checkout_name"
        session.customer.clear()
        return BotReply([self._cart_text(session) + "\n\n¿Cuál es tu nombre completo?"])

    def _confirmation(self, session: Session) -> BotReply:
        notes = session.customer.get("notes") or "Sin indicaciones"
        text = (
            f"*Vista previa de tu pedido*\n"
            f"Nombre: {session.customer['name']}\n"
            f"Documento: {session.customer['document']}\n"
            f"Ciudad: {session.customer['city']}\n"
            f"Dirección: {session.customer['address']}\n"
            f"Notas: {notes}\n\n{self._cart_text(session)}"
        )
        return BotReply([text], [self._confirm_buttons()])

    @staticmethod
    def _confirm_buttons() -> dict[str, Any]:
        return {
            "type": "buttons",
            "body": "¿Confirmas la creación del pedido?",
            "buttons": [
                {"id": "order:confirm", "title": "Confirmar pedido"},
                {"id": "order:cancel", "title": "Cancelar"},
            ],
        }

    def _complete_order(self, phone: str, session: Session) -> BotReply:
        total_items = sum(session.cart.values())
        volume_price = total_items >= self.volume_min_quantity
        items: list[dict[str, Any]] = []
        total = 0
        for sku, quantity in session.cart.items():
            product = self.catalog.by_sku[sku]
            unit_price = self._unit_price(product, volume_price)
            subtotal = unit_price * quantity
            total += subtotal
            items.append({
                "sku": sku,
                "name": product.name,
                "quantity": quantity,
                "unit_price": unit_price,
                "subtotal": subtotal,
                "variant_id": product.variant_id,
                "deposit_id": product.deposit_id,
            })
        order = {
            "id": f"VEL-{secrets.token_hex(3).upper()}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "phone": phone,
            "customer": dict(session.customer),
            "items": items,
            "total": total,
            "is_wholesale": volume_price,
            "status": "pending_sync",
        }
        return BotReply(order=order)

    def finalize_order(self, phone: str, order: dict[str, Any]) -> None:
        session = self.sessions.setdefault(phone, Session())
        order["status"] = "confirmed"
        self.orders.save(order)
        session.cart.clear()
        session.customer.clear()
        session.state = "menu"
        session.package_mode = False

    @staticmethod
    def _list(title: str, body: str, button: str, rows: list[dict[str, str]]) -> dict[str, Any]:
        return {
            "type": "list",
            "title": title,
            "body": body,
            "button": button,
            "sections": [{"title": title, "rows": rows[:10]}],
        }

    @staticmethod
    def _short(value: str, limit: int) -> str:
        value = " ".join(value.split())
        return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"
