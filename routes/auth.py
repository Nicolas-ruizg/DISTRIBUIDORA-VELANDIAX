from datetime import datetime

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Usuario
from schemas.auth_schema import AdminLoginRequest, AdminLoginResponse
from utils.jwt_handler import crear_token

router = APIRouter(prefix="/admin", tags=["auth"])


@router.post("/login", response_model=AdminLoginResponse)
def admin_login(data: AdminLoginRequest, db: Session = Depends(get_db)):
    usuario_db = db.scalar(
        select(Usuario).where(
            func.lower(Usuario.email) == data.email.strip().lower(),
            Usuario.activo.is_(True),
        )
    )

    if not usuario_db or not bcrypt.checkpw(
        data.password.encode(),
        usuario_db.password_hash.encode(),
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )

    if usuario_db.rol != "ADMINISTRADOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene permisos de administrador",
        )

    usuario_db.ultimo_acceso = datetime.now()
    db.commit()

    usuario = {
        "id_usuario": usuario_db.id_usuario,
        "nombre": usuario_db.nombre,
        "email": usuario_db.email,
        "rol": usuario_db.rol,
    }
    return {
        "success": True,
        "token": crear_token(usuario),
        "usuario": usuario,
    }
