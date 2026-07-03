from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Deposito
from routes.admin import ROL_ADMIN, normalizar_rol, verificar_admin, verificar_usuario_autenticado
from schemas.deposito import DepositoCreate, DepositoResponse, DepositoUpdate

router = APIRouter(prefix="/admin/depositos", tags=["depositos"])


def _serializar_deposito(deposito: Deposito):
    return {
        "id_deposito": deposito.id_deposito,
        "nombre": deposito.nombre,
        "activo": deposito.activo,
        "fecha_creacion": deposito.fecha_creacion,
    }


def _normalizar_id_deposito(id_deposito: str) -> str:
    id_normalizado = id_deposito.strip().upper()
    if not id_normalizado:
        raise HTTPException(status_code=400, detail="El id_deposito es obligatorio")
    return id_normalizado


@router.get("", response_model=list[DepositoResponse])
def listar_depositos(
    usuario: dict = Depends(verificar_usuario_autenticado),
    db: Session = Depends(get_db),
):
    consulta = select(Deposito).order_by(Deposito.id_deposito)
    if normalizar_rol(usuario.get("rol")) != ROL_ADMIN:
        id_deposito = usuario.get("id_deposito")
        if not id_deposito:
            return []
        consulta = consulta.where(
            Deposito.id_deposito == id_deposito,
            Deposito.activo.is_(True),
        )
    depositos = db.scalars(consulta).all()
    return [_serializar_deposito(deposito) for deposito in depositos]


@router.post("", response_model=DepositoResponse, status_code=status.HTTP_201_CREATED)
def crear_deposito(
    deposito: DepositoCreate,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    deposito_db = Deposito(
        id_deposito=_normalizar_id_deposito(deposito.id_deposito),
        nombre=deposito.nombre,
        activo=deposito.activo,
    )
    db.add(deposito_db)
    try:
        db.commit()
        db.refresh(deposito_db)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="No fue posible crear el deposito") from exc
    return _serializar_deposito(deposito_db)


@router.put("/{id_deposito}", response_model=DepositoResponse)
def actualizar_deposito(
    id_deposito: str,
    cambios_deposito: DepositoUpdate,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    deposito_db = db.get(Deposito, _normalizar_id_deposito(id_deposito))
    if not deposito_db:
        raise HTTPException(status_code=404, detail="Deposito no encontrado")

    cambios = cambios_deposito.model_dump(exclude_unset=True)
    if not cambios:
        raise HTTPException(status_code=400, detail="Debe enviar al menos un campo")
    for campo, valor in cambios.items():
        setattr(deposito_db, campo, valor)

    try:
        db.commit()
        db.refresh(deposito_db)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="No fue posible actualizar el deposito") from exc
    return _serializar_deposito(deposito_db)


@router.delete("/{id_deposito}", response_model=DepositoResponse)
def desactivar_deposito(
    id_deposito: str,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    deposito_db = db.get(Deposito, _normalizar_id_deposito(id_deposito))
    if not deposito_db:
        raise HTTPException(status_code=404, detail="Deposito no encontrado")
    deposito_db.activo = False
    db.commit()
    db.refresh(deposito_db)
    return _serializar_deposito(deposito_db)
