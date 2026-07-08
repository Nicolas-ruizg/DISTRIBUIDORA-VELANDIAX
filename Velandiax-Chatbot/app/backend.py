from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Any

import httpx

from app.catalog import Product
from app.config import Settings


class VelandiaxBackend:
    """Cliente HTTP para las rutas FastAPI existentes de Velandiax."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._token: str | None = None

    @property
    def configured(self) -> bool:
        return bool(self.settings.backend_api_url)

    async def fetch_catalog(self) -> list[Product]:
        async with httpx.AsyncClient(base_url=self.settings.backend_api_url, timeout=20) as client:
            response = await client.get("/productos")
            response.raise_for_status()
            summaries = response.json()
            details = await asyncio.gather(
                *(self._fetch_product(client, item["id_producto"]) for item in summaries)
            )
        products: list[Product] = []
        for detail in details:
            variants = [item for item in detail.get("variantes", []) if item.get("estado") == "ACTIVO"]
            for variant in variants:
                attributes = variant.get("atributos") or {}
                suffix = " / ".join(str(value) for value in attributes.values() if value)
                sku = detail["codigo_producto"]
                if len(variants) > 1:
                    sku = f"{sku}-V{variant['id_variante']}"
                name = detail["nombre"] + (f" — {suffix}" if suffix else "")
                searchable = tuple(
                    str(value) for value in (detail.get("categoria"), *attributes.values()) if value
                )
                image_url = (
                    variant.get("imagen_principal")
                    or next(
                        (image.get("url") for image in variant.get("imagenes", []) if image.get("es_principal")),
                        None,
                    )
                    or next((image.get("url") for image in variant.get("imagenes", [])), None)
                    or next(
                        (image.get("url") for image in detail.get("imagenes", []) if image.get("es_principal")),
                        None,
                    )
                    or next((image.get("url") for image in detail.get("imagenes", [])), None)
                )
                products.append(
                    Product(
                        sku=sku,
                        name=name,
                        description=detail.get("descripcion") or "",
                        price=int(Decimal(str(variant["precio_minorista"]))),
                        category=detail.get("categoria") or "",
                        keywords=searchable,
                        variant_id=variant["id_variante"],
                        product_id=detail["id_producto"],
                        deposit_id=detail.get("id_deposito"),
                        image_url=image_url,
                        category_id=detail.get("id_categoria"),
                        wholesale_price=int(Decimal(str(variant["precio_mayorista"]))),
                        previous_price=(
                            int(Decimal(str(detail["precio_anterior"])))
                            if detail.get("precio_anterior") is not None
                            else None
                        ),
                        on_sale=bool(detail.get("en_oferta")),
                        package_static=bool(detail.get("paquete_estatico")),
                        package_eligible=bool(variant.get("aplica_paquete")),
                        attributes=tuple((str(key), str(value)) for key, value in attributes.items()),
                    )
                )
        return products

    @staticmethod
    async def _fetch_product(client: httpx.AsyncClient, product_id: int) -> dict[str, Any]:
        response = await client.get(f"/productos/{product_id}")
        response.raise_for_status()
        return response.json()

    async def tracking(self, phone: str) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(base_url=self.settings.backend_api_url, timeout=20) as client:
            response = await client.get("/pedidos/seguimiento", params={"celular": phone})
            response.raise_for_status()
            return response.json()

    async def create_order(self, order: dict[str, Any]) -> dict[str, Any]:
        token = await self._login()
        variant_items = [item for item in order["items"] if item.get("variant_id")]
        if len(variant_items) != len(order["items"]):
            raise ValueError("El pedido contiene productos sin id_variante del backend")
        deposit_ids = {item.get("deposit_id") for item in variant_items if item.get("deposit_id")}
        if len(deposit_ids) != 1:
            raise ValueError("El pedido debe pertenecer a un único depósito")
        customer = order["customer"]
        payload = {
            "cliente": {
                "nombre": customer["name"],
                "cedula": customer["document"],
                "celular": order["phone"],
            },
            "id_deposito": next(iter(deposit_ids)),
            "canal_venta": "WEB",
            "tipo_envio": None,
            "estado": "PENDIENTE",
            "estado_pago": "CANCELADO",
            "precio_envio": 0,
            "es_mayorista": bool(order.get("is_wholesale")),
            "total": order["total"],
            "envio": None,
            "items": [
                {"id_variante": item["variant_id"], "cantidad": item["quantity"]}
                for item in variant_items
            ],
        }
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(base_url=self.settings.backend_api_url, timeout=20) as client:
            response = await client.post("/admin/pedidos", headers=headers, json=payload)
            if response.status_code == 401:
                self._token = None
                headers["Authorization"] = f"Bearer {await self._login()}"
                response = await client.post("/admin/pedidos", headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

    async def _login(self) -> str:
        if self._token:
            return self._token
        if not self.settings.backend_email or not self.settings.backend_password:
            raise ValueError("Faltan BACKEND_API_EMAIL y BACKEND_API_PASSWORD")
        async with httpx.AsyncClient(base_url=self.settings.backend_api_url, timeout=20) as client:
            response = await client.post(
                "/admin/login",
                json={"email": self.settings.backend_email, "password": self.settings.backend_password},
            )
            response.raise_for_status()
            self._token = response.json()["token"]
            return self._token
