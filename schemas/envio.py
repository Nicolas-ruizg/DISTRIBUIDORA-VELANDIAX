from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class EnvioCreate(BaseModel):
    transportadora: str = Field(default="VELANDIAX EXPRESS", min_length=2, max_length=120)
    numero_guia: Optional[str] = Field(default=None, min_length=3, max_length=120)
    nombre_destinatario: str = Field(min_length=2, max_length=200)
    celular_destinatario: Optional[str] = Field(default=None, max_length=20)
    direccion: str = Field(min_length=5)
    ciudad: str = Field(min_length=2, max_length=100)
    departamento: Optional[str] = Field(default=None, max_length=100)
    codigo_postal: Optional[str] = Field(default=None, max_length=20)
    notas: Optional[str] = None
    costo: Decimal = Field(default=Decimal("0"), ge=0)


class EnvioResponse(BaseModel):
    id_envio: int
    id_pedido: int
    transportadora: Optional[str] = None
    numero_guia: Optional[str] = None
    estado: str
    nombre_destinatario: str
    celular_destinatario: Optional[str] = None
    direccion: str
    ciudad: str
    departamento: Optional[str] = None
    codigo_postal: Optional[str] = None
    notas: Optional[str] = None
    costo: Decimal
    fecha_despacho: Optional[datetime] = None
    fecha_entrega: Optional[datetime] = None
    fecha_creacion: datetime


class SeguimientoEnvioResponse(BaseModel):
    numero_guia: str
    transportadora: Optional[str] = None
    estado: str
    ciudad: str
    fecha_despacho: Optional[datetime] = None
    fecha_entrega: Optional[datetime] = None
    fecha_creacion: datetime
