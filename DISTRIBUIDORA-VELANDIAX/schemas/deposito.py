from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DepositoCreate(BaseModel):
    id_deposito: str = Field(min_length=2, max_length=20)
    nombre: Optional[str] = Field(default=None, max_length=120)
    activo: bool = True


class DepositoUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, max_length=120)
    activo: Optional[bool] = None


class DepositoResponse(BaseModel):
    id_deposito: str
    nombre: Optional[str] = None
    activo: bool
    fecha_creacion: datetime
