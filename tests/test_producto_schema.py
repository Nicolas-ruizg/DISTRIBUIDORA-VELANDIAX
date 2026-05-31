from decimal import Decimal

import pytest
from pydantic import ValidationError

from schemas.producto import ModalidadVentaEnum, ProductoCreate, ProductoUpdate


def test_crear_producto_valido_usa_modalidad_ambas_por_defecto():
    producto = ProductoCreate(
        id_categoria=1,
        nombre_prenda="Camisa Oxford",
        precio_lista="95000.00",
        precio_minorista="85000.00",
        precio_mayorista="72000.00",
    )

    assert producto.modalidad_venta == ModalidadVentaEnum.AMBAS
    assert producto.precio_minorista == Decimal("85000.00")


def test_rechazar_precio_negativo():
    with pytest.raises(ValidationError):
        ProductoCreate(
            nombre_prenda="Camisa Oxford",
            precio_lista="-1",
            precio_minorista="85000.00",
            precio_mayorista="72000.00",
        )


def test_rechazar_modalidad_desconocida():
    with pytest.raises(ValidationError):
        ProductoCreate(
            nombre_prenda="Camisa Oxford",
            modalidad_venta="MAYOREO",
            precio_lista="95000.00",
            precio_minorista="85000.00",
            precio_mayorista="72000.00",
        )


def test_actualizacion_parcial_no_exige_todos_los_campos():
    producto = ProductoUpdate(activo=False)

    assert producto.model_dump(exclude_none=True) == {"activo": False}

