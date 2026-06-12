from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, Field


class ProductoCreate(BaseModel):
    id_categoria: int = Field(gt=0)
    nombre: str = Field(min_length=2, max_length=160)
    descripcion: Optional[str] = None
    paquete_estatico: bool = False


class ProductoUpdate(BaseModel):
    id_categoria: Optional[int] = Field(None, gt=0)
    nombre: Optional[str] = Field(None, min_length=2, max_length=160)
    descripcion: Optional[str] = None
    paquete_estatico: Optional[bool] = None


class VarianteCreate(BaseModel):
    precio_costo: Decimal = Field(ge=0)
    precio_minorista: Decimal = Field(ge=0)
    precio_mayorista: Decimal = Field(ge=0)
    peso: Optional[Decimal] = Field(None, ge=0)
    aplica_paquete: bool = False
    atributos: dict[str, Any] = Field(default_factory=dict)


class VarianteUpdate(BaseModel):
    precio_costo: Optional[Decimal] = Field(None, ge=0)
    precio_minorista: Optional[Decimal] = Field(None, ge=0)
    precio_mayorista: Optional[Decimal] = Field(None, ge=0)
    peso: Optional[Decimal] = Field(None, ge=0)
    aplica_paquete: Optional[bool] = None
    atributos: Optional[dict[str, Any]] = None


class ProductoResumenResponse(BaseModel):
    id_producto: int
    id_categoria: int
    categoria: str
    nombre: str
    descripcion: Optional[str] = None
    paquete_estatico: bool
    variantes: int
    precio_desde: Optional[Decimal] = None


class VarianteProductoResponse(BaseModel):
    id_variante: int
    precio_costo: Decimal
    precio_minorista: Decimal
    precio_mayorista: Decimal
    peso: Optional[Decimal] = None
    aplica_paquete: bool
    atributos: dict[str, Any]


class ProductoDetalleResponse(BaseModel):
    id_producto: int
    id_categoria: int
    categoria: str
    nombre: str
    descripcion: Optional[str] = None
    paquete_estatico: bool
    variantes: list[VarianteProductoResponse]
