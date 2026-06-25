from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Categoria
from routes.admin import verificar_admin
from schemas.categoria import CategoriaCreate, CategoriaResponse, CategoriaUpdate

router = APIRouter(tags=["categorias"])


def _serializar_categoria(categoria: Categoria):
    return {
        "id_categoria": categoria.id_categoria,
        "nombre": categoria.nombre,
        "descripcion": categoria.descripcion,
    }


@router.get("/categorias", response_model=list[CategoriaResponse])
@router.get("/admin/categorias", response_model=list[CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    categorias = db.scalars(select(Categoria).order_by(Categoria.nombre)).all()
    return [_serializar_categoria(categoria) for categoria in categorias]


@router.get("/categorias/{id_categoria}", response_model=CategoriaResponse)
@router.get("/admin/categorias/{id_categoria}", response_model=CategoriaResponse)
def obtener_categoria(id_categoria: int, db: Session = Depends(get_db)):
    categoria = db.get(Categoria, id_categoria)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria no encontrada",
        )
    return _serializar_categoria(categoria)


@router.post(
    "/admin/categorias",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_categoria(
    categoria: CategoriaCreate,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    categoria_db = Categoria(
        nombre=categoria.nombre,
        descripcion=categoria.descripcion,
    )
    db.add(categoria_db)
    try:
        db.commit()
        db.refresh(categoria_db)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No fue posible crear la categoria",
        ) from exc
    return _serializar_categoria(categoria_db)


@router.put("/admin/categorias/{id_categoria}", response_model=CategoriaResponse)
def actualizar_categoria(
    id_categoria: int,
    categoria: CategoriaUpdate,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    cambios = categoria.model_dump(exclude_none=True)
    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )

    categoria_db = db.get(Categoria, id_categoria)
    if not categoria_db:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")

    for campo, valor in cambios.items():
        setattr(categoria_db, campo, valor)
    try:
        db.commit()
        db.refresh(categoria_db)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="No fue posible actualizar la categoria") from exc
    return _serializar_categoria(categoria_db)


@router.delete("/admin/categorias/{id_categoria}", response_model=dict)
def eliminar_categoria(
    id_categoria: int,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    categoria_db = db.get(Categoria, id_categoria)
    if not categoria_db:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")

    db.delete(categoria_db)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="No fue posible eliminar la categoria") from exc
    return {"success": True, "id_categoria": id_categoria}
