from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, Field


class ProductoCreate(BaseModel):
    id_categoria: int = Field(gt=0)
    id_deposito: str = Field(default="DEP001", min_length=2, max_length=20)
    codigo_producto: str = Field(min_length=2, max_length=60)
    nombre: str = Field(min_length=2, max_length=160)
    descripcion: Optional[str] = None
    paquete_estatico: bool = False
    en_oferta: bool = False
    precio_anterior: Optional[float] = Field(default=None, ge=0)
    estado: str = Field(default="ACTIVO", pattern="^(ACTIVO|INACTIVO)$")


class ProductoUpdate(BaseModel):
    id_categoria: Optional[int] = Field(None, gt=0)
    id_deposito: Optional[str] = Field(None, min_length=2, max_length=20)
    codigo_producto: Optional[str] = Field(None, min_length=2, max_length=60)
    nombre: Optional[str] = Field(None, min_length=2, max_length=160)
    descripcion: Optional[str] = None
    paquete_estatico: Optional[bool] = None
    en_oferta: Optional[bool] = None
    precio_anterior: Optional[float] = Field(default=None, ge=0)
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
    codigo_producto: str
    id_categoria: int
    categoria: str
    id_deposito: str
    deposito: Optional[str] = None
    nombre: str
    descripcion: Optional[str] = None
    paquete_estatico: bool
    en_oferta: bool
    precio_anterior: Optional[float] = None
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
    codigo_producto: str
    id_categoria: int
    categoria: str
    id_deposito: str
    deposito: Optional[str] = None
    nombre: str
    descripcion: Optional[str] = None
    paquete_estatico: bool
    en_oferta: bool
    precio_anterior: Optional[float] = None
    estado: str
    imagenes: list[ImagenProductoResponse]
    variantes: list[VarianteProductoResponse]
