import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from database.connection import get_db
from database.models import Deposito, Usuario
from routes.admin import ROLES_VALIDOS
from routes.admin import verificar_admin
from schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate

router = APIRouter(prefix="/admin/usuarios", tags=["usuarios"])


def _serializar_usuario(usuario: Usuario):
    return {
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "id_deposito": usuario.id_deposito,
        "deposito": usuario.deposito.nombre if usuario.deposito else None,
        "codigo_cuenta": usuario.codigo_cuenta,
        "rol": usuario.rol,
        "activo": usuario.activo,
        "fecha_creacion": usuario.fecha_creacion,
        "ultimo_acceso": usuario.ultimo_acceso,
    }


def _normalizar_rol(rol: str) -> str:
    rol_normalizado = rol.strip().upper()
    if rol_normalizado not in ROLES_VALIDOS:
        raise HTTPException(status_code=400, detail="Rol de usuario invalido")
    return rol_normalizado


def _normalizar_codigo_cuenta(codigo: str | None) -> str | None:
    if codigo is None:
        return None
    codigo_normalizado = codigo.strip().upper()
    return codigo_normalizado or None


def _validar_deposito(db: Session, id_deposito: str | None) -> str | None:
    if id_deposito is None:
        return None
    id_normalizado = id_deposito.strip().upper()
    if not id_normalizado:
        return None
    deposito = db.get(Deposito, id_normalizado)
    if not deposito or not deposito.activo:
        raise HTTPException(status_code=404, detail="Deposito no encontrado o inactivo")
    return id_normalizado


@router.get("", response_model=list[UsuarioResponse])
def listar_usuarios(
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    usuarios = db.scalars(
        select(Usuario).options(joinedload(Usuario.deposito)).order_by(Usuario.nombre)
    ).all()
    return [_serializar_usuario(usuario_db) for usuario_db in usuarios]


@router.get("/{id_usuario}", response_model=UsuarioResponse)
def obtener_usuario(
    id_usuario: int,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    usuario_db = db.scalar(
        select(Usuario)
        .options(joinedload(Usuario.deposito))
        .where(Usuario.id_usuario == id_usuario)
    )
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return _serializar_usuario(usuario_db)


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    nuevo_usuario: UsuarioCreate,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    usuario_db = Usuario(
        nombre=nuevo_usuario.nombre,
        email=nuevo_usuario.email.lower(),
        id_deposito=_validar_deposito(db, nuevo_usuario.id_deposito),
        codigo_cuenta=_normalizar_codigo_cuenta(nuevo_usuario.codigo_cuenta),
        password_hash=bcrypt.hashpw(
            nuevo_usuario.password.encode(),
            bcrypt.gensalt(),
        ).decode(),
        rol=_normalizar_rol(nuevo_usuario.rol),
        activo=True,
    )
    db.add(usuario_db)
    try:
        db.commit()
        db.refresh(usuario_db)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No fue posible crear el usuario. Verifique que el email no exista.",
        ) from exc
    return _serializar_usuario(usuario_db)


@router.put("/{id_usuario}", response_model=UsuarioResponse)
def actualizar_usuario(
    id_usuario: int,
    cambios_usuario: UsuarioUpdate,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    cambios = cambios_usuario.model_dump(exclude_none=True)
    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )

    usuario_db = db.get(Usuario, id_usuario)
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if "password" in cambios:
        cambios["password_hash"] = bcrypt.hashpw(
            cambios.pop("password").encode(),
            bcrypt.gensalt(),
        ).decode()
    if "email" in cambios:
        cambios["email"] = cambios["email"].lower()
    if "id_deposito" in cambios:
        cambios["id_deposito"] = _validar_deposito(db, cambios["id_deposito"])
    if "codigo_cuenta" in cambios:
        cambios["codigo_cuenta"] = _normalizar_codigo_cuenta(cambios["codigo_cuenta"])
    if "rol" in cambios:
        cambios["rol"] = _normalizar_rol(cambios["rol"])
    for campo, valor in cambios.items():
        setattr(usuario_db, campo, valor)

    try:
        db.commit()
        db.refresh(usuario_db)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="No fue posible actualizar el usuario") from exc
    return _serializar_usuario(usuario_db)


@router.delete("/{id_usuario}", response_model=UsuarioResponse)
def desactivar_usuario(
    id_usuario: int,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    if id_usuario == usuario.get("id_usuario"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puede desactivar su propio usuario",
        )

    usuario_db = db.get(Usuario, id_usuario)
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario_db.activo = False
    db.commit()
    db.refresh(usuario_db)
    return _serializar_usuario(usuario_db)
