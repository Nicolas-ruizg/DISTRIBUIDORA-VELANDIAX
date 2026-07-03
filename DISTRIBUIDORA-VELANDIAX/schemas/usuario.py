from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UsuarioCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    email: str = Field(pattern=r"^[\w.+'-]+@[\w.-]+\.[A-Za-z]{2,}$", max_length=160)
    id_deposito: Optional[str] = Field(default=None, min_length=2, max_length=20)
    codigo_cuenta: Optional[str] = Field(default=None, min_length=3, max_length=20)
    password: str = Field(min_length=8, max_length=128)
    rol: str = Field(default="ADMINISTRADOR", pattern="^(ADMINISTRADOR|VENDEDOR|INVENTARIO)$")


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=150)
    email: Optional[str] = Field(
        None,
        pattern=r"^[\w.+'-]+@[\w.-]+\.[A-Za-z]{2,}$",
        max_length=160,
    )
    id_deposito: Optional[str] = Field(None, min_length=2, max_length=20)
    codigo_cuenta: Optional[str] = Field(None, min_length=3, max_length=20)
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    rol: Optional[str] = Field(None, pattern="^(ADMINISTRADOR|VENDEDOR|INVENTARIO)$")
    activo: Optional[bool] = None


class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    email: str
    id_deposito: Optional[str] = None
    deposito: Optional[str] = None
    codigo_cuenta: Optional[str] = None
    rol: str
    activo: bool
    fecha_creacion: datetime
    ultimo_acceso: Optional[datetime] = None
