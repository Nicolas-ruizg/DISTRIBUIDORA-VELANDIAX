from typing import Optional

from pydantic import BaseModel, Field


class CategoriaCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    descripcion: Optional[str] = None


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=120)
    descripcion: Optional[str] = None


class CategoriaResponse(BaseModel):
    id_categoria: int
    nombre: str
    descripcion: Optional[str] = None
