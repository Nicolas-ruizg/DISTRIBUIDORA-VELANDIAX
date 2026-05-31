import os
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple

from schemas.venta_schema import ProductoVentaItem

CENTAVOS = Decimal("0.01")


def redondear_moneda(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


class CalculadoraVenta:
    @staticmethod
    def calcular_subtotal_linea(producto: ProductoVentaItem) -> Decimal:
        precio_linea = producto.cantidad * producto.precio_unitario
        descuento = precio_linea * producto.descuento_porcentaje / Decimal("100")
        return redondear_moneda(precio_linea - descuento)

    @staticmethod
    def calcular_totales(
        productos: List[ProductoVentaItem],
        impuesto_porcentaje: Decimal = Decimal("19"),
    ) -> Dict[str, Decimal]:
        subtotal = Decimal("0")
        descuento_total = Decimal("0")

        for producto in productos:
            precio_linea = producto.cantidad * producto.precio_unitario
            descuento_linea = (
                precio_linea * producto.descuento_porcentaje / Decimal("100")
            )
            subtotal += precio_linea
            descuento_total += descuento_linea

        subtotal_con_descuento = subtotal - descuento_total
        impuesto = subtotal_con_descuento * impuesto_porcentaje / Decimal("100")
        total = subtotal_con_descuento + impuesto

        return {
            "subtotal": redondear_moneda(subtotal),
            "descuento_total": redondear_moneda(descuento_total),
            "subtotal_con_descuento": redondear_moneda(subtotal_con_descuento),
            "impuesto": redondear_moneda(impuesto),
            "total": redondear_moneda(total),
        }

    @staticmethod
    def generar_numero_venta(id_venta: int, anio: int = None) -> str:
        anio = anio or datetime.now().year
        return f"VTA-{anio}-{id_venta:07d}"

    @staticmethod
    def validar_productos(productos: List[ProductoVentaItem]) -> Tuple[bool, str]:
        max_productos = int(os.getenv("MAX_PRODUCTOS_POR_VENTA", "100"))
        max_cantidad = int(os.getenv("MAX_CANTIDAD_TOTAL_POR_VENTA", "10000"))

        if not productos:
            return False, "Debe incluir al menos 1 producto"

        if len(productos) > max_productos:
            return False, f"Maximo {max_productos} productos por venta"

        total_cantidad = sum(producto.cantidad for producto in productos)
        if total_cantidad > max_cantidad:
            return False, "Cantidad total de productos excede el limite"

        return True, "Validacion exitosa"


calculadora = CalculadoraVenta()

