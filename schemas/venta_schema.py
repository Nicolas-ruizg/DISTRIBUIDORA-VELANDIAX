from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class FormaPagoEnum(str, Enum):
    EFECTIVO = "efectivo"
    TRANSFERENCIA = "transferencia"
    TARJETA_CREDITO = "tarjeta_credito"
    TARJETA_DEBITO = "tarjeta_debito"
    CHEQUE = "cheque"


class EstadoVentaEnum(str, Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    ENTREGADA = "entregada"
    CANCELADA = "cancelada"


class ProductoVentaItem(BaseModel):
    id_producto: int = Field(gt=0)
    nombre_producto: str = Field(min_length=1, max_length=150)
    cantidad: int = Field(gt=0, description="Cantidad debe ser mayor a 0")
    precio_unitario: Decimal = Field(gt=0, description="Precio debe ser mayor a 0")
    descuento_porcentaje: Decimal = Field(default=Decimal("0"), ge=0, le=100)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id_producto": 1,
                "nombre_producto": "Producto XYZ",
                "cantidad": 5,
                "precio_unitario": 100.00,
                "descuento_porcentaje": 10,
            }
        }
    )


class ClienteInfo(BaseModel):
    nombre: str = Field(min_length=3, max_length=100)
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    telefono: Optional[str] = Field(None, pattern=r"^\+?[\d\s\-]{7,}$")
    empresa: Optional[str] = Field(None, max_length=150)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Juan Perez",
                "email": "juan@example.com",
                "telefono": "+57 300 123 4567",
                "empresa": "Empresa XYZ",
            }
        }
    )


class VentaCreate(BaseModel):
    cliente: ClienteInfo
    productos: List[ProductoVentaItem] = Field(min_length=1, max_length=100)
    forma_pago: FormaPagoEnum
    impuesto_porcentaje: Decimal = Field(default=Decimal("19"), ge=0, le=100)
    notas: Optional[str] = Field(None, max_length=500)
    referencia_externa: Optional[str] = Field(None, max_length=50)


class VentaResponse(BaseModel):
    id_venta: int
    numero_venta: str
    cliente: ClienteInfo
    productos: List[ProductoVentaItem]
    forma_pago: str
    estado: str
    subtotal: Decimal
    descuento_total: Decimal
    impuesto: Decimal
    total: Decimal
    fecha_creacion: datetime
    vendedor: str

