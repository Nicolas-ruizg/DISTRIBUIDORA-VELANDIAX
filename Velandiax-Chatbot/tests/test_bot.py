from pathlib import Path

from app.bot import SalesBot
from app.catalog import Catalog, Product
from app.gemini import IntentDecision
from app.storage import OrderRepository


def make_bot(tmp_path: Path) -> SalesBot:
    catalog = Catalog(
        [
            Product(
                "SKU-1",
                "Camiseta prueba talla M",
                "Para uso diario",
                10000,
                "Camisetas",
                ("diario", "negra"),
                variant_id=1,
                product_id=1,
                deposit_id="DEP001",
                category_id=1,
                wholesale_price=7000,
                package_eligible=True,
                attributes=(("Talla", "M"), ("Color", "Negro")),
            )
        ]
    )
    return SalesBot(catalog, OrderRepository(tmp_path / "orders.jsonl"))


def test_complete_purchase_flow_with_interactive_messages(tmp_path: Path) -> None:
    bot = make_bot(tmp_path)
    phone = "573001234567"

    welcome = bot.handle(phone, "hola")
    assert welcome.interactive[0]["type"] == "buttons"
    store = bot.handle(phone, "menu:shop")
    assert store.interactive[0]["type"] == "list"
    detail = bot.handle(phone, "product:SKU-1")
    assert detail.interactive[-1]["type"] == "buttons"
    quantity_menu = bot.handle(phone, "quantity:SKU-1")
    assert quantity_menu.interactive[0]["type"] == "list"
    added = bot.handle(phone, "qty:add:SKU-1:5")
    assert "Total: $50.000" in added.messages[0]

    bot.handle(phone, "checkout:start")
    bot.handle(phone, "Ada Lovelace")
    bot.handle(phone, "123456789")
    bot.handle(phone, "Bogotá")
    bot.handle(phone, "Calle 1 # 2-3")
    confirmation = bot.handle(phone, "NO")
    assert "Ada Lovelace" in confirmation.messages[0]
    result = bot.handle(phone, "order:confirm")

    assert result.order is not None
    assert result.order["phone"] == phone
    assert result.order["total"] == 50000
    bot.finalize_order(phone, result.order)
    assert (tmp_path / "orders.jsonl").exists()


def test_volume_price_starts_at_fifty_items_and_is_not_exposed(tmp_path: Path) -> None:
    bot = make_bot(tmp_path)
    phone = "1"
    result = bot.handle_ai(
        phone,
        IntentDecision("add_product", product_reference="SKU-1", quantity=50),
    )
    assert "Precio especial por volumen aplicado" in result.messages[0]
    assert "mayorista" not in result.messages[0].lower()
    assert "Total: $350.000" in result.messages[0]


def test_custom_quantity_and_cart_edit(tmp_path: Path) -> None:
    bot = make_bot(tmp_path)
    phone = "1"
    bot.handle(phone, "qty:add:SKU-1:custom")
    result = bot.handle(phone, "37")
    assert "37 ×" in result.messages[0]
    bot.handle(phone, "qty:set:SKU-1:custom")
    changed = bot.handle(phone, "12")
    assert "12 ×" in changed.messages[0]


def test_ai_search_returns_real_product(tmp_path: Path) -> None:
    bot = make_bot(tmp_path)
    response = bot.handle_ai(
        "1",
        IntentDecision("product_search", query="camiseta negra talla M"),
    )
    rows = response.interactive[0]["sections"][0]["rows"]
    assert rows[0]["id"] == "product:SKU-1"
