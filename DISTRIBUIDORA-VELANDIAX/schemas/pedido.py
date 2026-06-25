from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel
from pydantic import Field

from schemas.envio import EnvioCreate


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
    estado_pago: str = Field(default="CANCELADO", min_length=2, max_length=20)
    precio_envio: Decimal = Field(default=Decimal("0"), ge=0)
    es_mayorista: bool = False
    total: Optional[Decimal] = Field(default=None, ge=0)
    envio: Optional[EnvioCreate] = None


class PedidoUpdate(BaseModel):
    estado: Optional[str] = Field(None, min_length=2, max_length=80)
    estado_pago: Optional[str] = Field(None, min_length=2, max_length=20)
    total: Optional[Decimal] = Field(None, ge=0)
    precio_envio: Optional[Decimal] = Field(None, ge=0)
    es_mayorista: Optional[bool] = None
    envio: Optional[EnvioCreate] = None


class PedidoResumenResponse(BaseModel):
    id_pedido: int
    id_cliente: int
    cliente: str
    celular: Optional[str] = None
    estado: str
    estado_pago: str
    numero_guia: Optional[str] = None
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


class PedidoSeguimientoResponse(BaseModel):
    id_pedido: int
    estado: str
    estado_pago: str
    numero_guia: Optional[str] = None
    estado_envio: Optional[str] = None
    transportadora: Optional[str] = None
    total: Decimal
    fecha: datetime
    items: int
