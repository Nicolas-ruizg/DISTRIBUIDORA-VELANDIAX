from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, Field


class ProductoCreate(BaseModel):
    id_categoria: int = Field(gt=0)
    nombre: str = Field(min_length=2, max_length=160)
    descripcion: Optional[str] = None
    paquete_estatico: bool = False
    estado: str = Field(default="ACTIVO", pattern="^(ACTIVO|INACTIVO)$")


class ProductoUpdate(BaseModel):
    id_categoria: Optional[int] = Field(None, gt=0)
    nombre: Optional[str] = Field(None, min_length=2, max_length=160)
    descripcion: Optional[str] = None
    paquete_estatico: Optional[bool] = None
    estado: Optional[str] = Field(None, pattern="^(ACTIVO|INACTIVO)$")


class ImagenProductoCreate(BaseModel):
    url: str = Field(min_length=5, max_length=500)
    alt_text: Optional[str] = Field(default=None, max_length=200)
    es_principal: bool = False
    orden: int = Field(default=0, ge=0)
    estado: str = Field(default="ACTIVO", pattern="^(ACTIVO|INACTIVO)$")


class ImagenProductoUpdate(BaseModel):
    url: Optional[str] = Field(default=None, min_length=5, max_length=500)
    alt_text: Optional[str] = Field(default=None, max_length=200)
    es_principal: Optional[bool] = None
    orden: Optional[int] = Field(default=None, ge=0)
    estado: Optional[str] = Field(None, pattern="^(ACTIVO|INACTIVO)$")


class ImagenProductoResponse(BaseModel):
    id_imagen: int
    url: str
    alt_text: Optional[str] = None
    es_principal: bool
    orden: int
    estado: str


class ImagenVarianteCreate(BaseModel):
    url: str = Field(min_length=5, max_length=500)
    alt_text: Optional[str] = Field(default=None, max_length=200)
    es_principal: bool = False
    orden: int = Field(default=0, ge=0)
    estado: str = Field(default="ACTIVO", pattern="^(ACTIVO|INACTIVO)$")


class ImagenVarianteUpdate(BaseModel):
    url: Optional[str] = Field(default=None, min_length=5, max_length=500)
    alt_text: Optional[str] = Field(default=None, max_length=200)
    es_principal: Optional[bool] = None
    orden: Optional[int] = Field(default=None, ge=0)
    estado: Optional[str] = Field(None, pattern="^(ACTIVO|INACTIVO)$")


class ImagenVarianteResponse(BaseModel):
    id_imagen_variante: int
    url: str
    alt_text: Optional[str] = None
    es_principal: bool
    orden: int
    estado: str


class VarianteCreate(BaseModel):
    precio_costo: Decimal = Field(ge=0)
    precio_minorista: Decimal = Field(ge=0)
    precio_mayorista: Decimal = Field(ge=0)
    peso: Optional[Decimal] = Field(None, ge=0)
    aplica_paquete: bool = False
    atributos: dict[str, Any] = Field(default_factory=dict)
    estado: str = Field(default="ACTIVO", pattern="^(ACTIVO|INACTIVO)$")


class VarianteUpdate(BaseModel):
    precio_costo: Optional[Decimal] = Field(None, ge=0)
    precio_minorista: Optional[Decimal] = Field(None, ge=0)
    precio_mayorista: Optional[Decimal] = Field(None, ge=0)
    peso: Optional[Decimal] = Field(None, ge=0)
    aplica_paquete: Optional[bool] = None
    atributos: Optional[dict[str, Any]] = None
    estado: Optional[str] = Field(None, pattern="^(ACTIVO|INACTIVO)$")


class ProductoResumenResponse(BaseModel):
    id_producto: int
    id_categoria: int
    categoria: str
    nombre: str
    descripcion: Optional[str] = None
    paquete_estatico: bool
    estado: str
    variantes: int
    precio_desde: Optional[Decimal] = None
    imagen_principal: Optional[str] = None


class VarianteProductoResponse(BaseModel):
    id_variante: int
    estado: str
    precio_costo: Decimal
    precio_minorista: Decimal
    precio_mayorista: Decimal
    peso: Optional[Decimal] = None
    aplica_paquete: bool
    atributos: dict[str, Any]
    imagen_principal: Optional[str] = None
    imagenes: list[ImagenVarianteResponse] = []


class ProductoDetalleResponse(BaseModel):
    id_producto: int
    id_categoria: int
    categoria: str
    nombre: str
    descripcion: Optional[str] = None
    paquete_estatico: bool
    estado: str
    imagenes: list[ImagenProductoResponse]
    variantes: list[VarianteProductoResponse]
