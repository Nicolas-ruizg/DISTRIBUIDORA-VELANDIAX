from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel
from pydantic import Field


class PedidoUpdate(BaseModel):
    estado: Optional[str] = Field(None, min_length=2, max_length=80)
    total: Optional[Decimal] = Field(None, ge=0)
    precio_envio: Optional[Decimal] = Field(None, ge=0)
    es_mayorista: Optional[bool] = None


class PedidoResumenResponse(BaseModel):
    id_pedido: int
    id_cliente: int
    cliente: str
    celular: Optional[str] = None
    estado: str
    total: Decimal
    precio_envio: Decimal
    es_mayorista: bool
    fecha: datetime
    items: int


class PedidoItemResponse(BaseModel):
    id_item_pedido: int
    id_variante: int
    id_producto: int
    producto: str
    cantidad: int
    precio_unitario: Decimal
    atributos: dict[str, Any]


class PedidoDetalleResponse(PedidoResumenResponse):
    items_detalle: list[PedidoItemResponse]
