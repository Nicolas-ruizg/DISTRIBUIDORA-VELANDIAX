from typing import Optional

from pydantic import BaseModel, Field


class CategoriaCreate(BaseModel):
    nombre_categoria: str = Field(min_length=2, max_length=100)


class CategoriaUpdate(BaseModel):
    nombre_categoria: Optional[str] = Field(None, min_length=2, max_length=100)
    activa: Optional[bool] = None


class CategoriaResponse(BaseModel):
    id_categoria: int
    nombre_categoria: str
    activa: bool

