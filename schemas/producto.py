from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ModalidadVentaEnum(str, Enum):
    SOLO_MINORISTA = "SOLO_MINORISTA"
    SOLO_MAYORISTA = "SOLO_MAYORISTA"
    AMBAS = "AMBAS"


class ProductoCreate(BaseModel):
    id_categoria: Optional[int] = Field(None, gt=0)
    nombre_prenda: str = Field(min_length=2, max_length=150)
    descripcion: Optional[str] = Field(None, max_length=1000)
    url_imagen: Optional[str] = Field(None, max_length=500)
    modalidad_venta: ModalidadVentaEnum = ModalidadVentaEnum.AMBAS
    precio_lista: Decimal = Field(gt=0)
    precio_minorista: Decimal = Field(gt=0)
    precio_mayorista: Decimal = Field(gt=0)
    url_producto: Optional[str] = Field(None, max_length=500)


class ProductoUpdate(BaseModel):
    id_categoria: Optional[int] = Field(None, gt=0)
    nombre_prenda: Optional[str] = Field(None, min_length=2, max_length=150)
    descripcion: Optional[str] = Field(None, max_length=1000)
    url_imagen: Optional[str] = Field(None, max_length=500)
    modalidad_venta: Optional[ModalidadVentaEnum] = None
    precio_lista: Optional[Decimal] = Field(None, gt=0)
    precio_minorista: Optional[Decimal] = Field(None, gt=0)
    precio_mayorista: Optional[Decimal] = Field(None, gt=0)
    activo: Optional[bool] = None
    url_producto: Optional[str] = Field(None, max_length=500)


class ProductoResponse(BaseModel):
    id_producto: int
    id_categoria: Optional[int]
    nombre_prenda: str
    descripcion: Optional[str]
    url_imagen: Optional[str]
    modalidad_venta: ModalidadVentaEnum
    precio_lista: Decimal
    precio_minorista: Decimal
    precio_mayorista: Decimal
    activo: bool
    url_producto: Optional[str]

