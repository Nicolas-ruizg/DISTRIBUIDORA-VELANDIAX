import hmac
import os

from fastapi import APIRouter, HTTPException, status

from schemas.auth_schema import AdminLoginRequest, AdminLoginResponse
from utils.jwt_handler import crear_token

router = APIRouter(prefix="/admin", tags=["auth"])


@router.post("/login", response_model=AdminLoginResponse)
def admin_login(data: AdminLoginRequest):
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_email or not admin_password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Credenciales admin no configuradas",
        )

    email_ok = hmac.compare_digest(data.email.strip().lower(), admin_email.lower())
    password_ok = hmac.compare_digest(data.password, admin_password)

    if not email_ok or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )

    usuario = {
        "id_usuario": 1,
        "nombre": "Administrador",
        "email": admin_email,
        "rol": "ADMINISTRADOR",
    }

    return {
        "success": True,
        "token": crear_token(usuario),
        "usuario": usuario,
    }
