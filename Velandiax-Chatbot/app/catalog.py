from __future__ import annotations

import json
import unicodedata
from dataclasses import dataclass
from pathlib import Path


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.lower())
    return "".join(char for char in value if not unicodedata.combining(char)).strip()


def money(value: int) -> str:
    return f"${value:,.0f}".replace(",", ".")


@dataclass(frozen=True, slots=True)
class Product:
    sku: str
    name: str
    description: str
    price: int
    category: str
    keywords: tuple[str, ...]
    variant_id: int | None = None
    product_id: int | None = None
    deposit_id: str | None = None
    image_url: str | None = None
    category_id: int | None = None
    wholesale_price: int | None = None
    previous_price: int | None = None
    on_sale: bool = False
    package_static: bool = False
    package_eligible: bool = False
    attributes: tuple[tuple[str, str], ...] = ()


class Catalog:
    def __init__(self, products: list[Product]):
        self.products = products
        self.by_sku = {product.sku.upper(): product for product in products}

    def replace(self, products: list[Product]) -> None:
        self.products = products
        self.by_sku = {product.sku.upper(): product for product in products}

    @classmethod
    def from_file(cls, path: Path) -> "Catalog":
        records = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            [
                Product(
                    sku=item["sku"],
                    name=item["name"],
                    description=item["description"],
                    price=int(item["price"]),
                    category=item["category"],
                    keywords=tuple(item.get("keywords", [])),
                )
                for item in records
            ]
        )

    def find(self, reference: str) -> Product | None:
        reference = reference.strip()
        if reference.isdigit():
            index = int(reference) - 1
            return self.products[index] if 0 <= index < len(self.products) else None
        return self.by_sku.get(reference.upper())

    def recommend(self, need: str, limit: int = 3) -> list[Product]:
        words = set(normalize(need).split())

        def score(product: Product) -> int:
            searchable = " ".join(
                (product.name, product.description, product.category, *product.keywords)
            )
            normalized = normalize(searchable)
            return sum(1 for word in words if len(word) > 2 and word in normalized)

        ranked = sorted(self.products, key=score, reverse=True)
        matches = [product for product in ranked if score(product) > 0]
        return (matches or ranked)[:limit]

    def search(self, query: str, limit: int = 8) -> list[Product]:
        normalized_query = normalize(query)
        words = {word for word in normalized_query.split() if len(word) > 1}
        if not words:
            return self.products[:limit]

        def score(product: Product) -> int:
            attributes = " ".join(f"{key} {value}" for key, value in product.attributes)
            searchable = normalize(
                " ".join(
                    (
                        product.sku,
                        product.name,
                        product.description,
                        product.category,
                        attributes,
                        *product.keywords,
                    )
                )
            )
            value = sum(
                3 if word in normalize(product.name) else 1
                for word in words
                if word in searchable
            )
            if normalized_query in searchable:
                value += 4
            return value

        ranked = sorted(self.products, key=score, reverse=True)
        return [product for product in ranked if score(product) > 0][:limit]

    def categories(self) -> list[tuple[int, str]]:
        values = {
            (product.category_id, product.category)
            for product in self.products
            if product.category_id is not None
        }
        return sorted(values, key=lambda item: normalize(item[1]))
