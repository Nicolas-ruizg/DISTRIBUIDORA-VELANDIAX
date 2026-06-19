from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UsuarioCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    email: str = Field(pattern=r"^[\w.+'-]+@[\w.-]+\.[A-Za-z]{2,}$", max_length=160)
    password: str = Field(min_length=8, max_length=128)


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=150)
    email: Optional[str] = Field(
        None,
        pattern=r"^[\w.+'-]+@[\w.-]+\.[A-Za-z]{2,}$",
        max_length=160,
    )
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    activo: Optional[bool] = None


class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    email: str
    rol: str
    activo: bool
    fecha_creacion: datetime
    ultimo_acceso: Optional[datetime] = None
