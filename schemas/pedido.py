from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel
from pydantic import Field


class PedidoClienteCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=200)
    celular: Optional[str] = Field(default=None, max_length=20)


class PedidoItemCreate(BaseModel):
    id_variante: int = Field(gt=0)
    cantidad: int = Field(gt=0)
    precio_unitario: Optional[Decimal] = Field(default=None, ge=0)


class PedidoCreate(BaseModel):
    id_cliente: Optional[int] = Field(default=None, gt=0)
    cliente: Optional[PedidoClienteCreate] = None
    items: list[PedidoItemCreate] = Field(min_length=1)
    estado: str = Field(default="PENDIENTE", min_length=2, max_length=30)
    precio_envio: Decimal = Field(default=Decimal("0"), ge=0)
    es_mayorista: bool = False
    total: Optional[Decimal] = Field(default=None, ge=0)


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
