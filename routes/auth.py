import bcrypt
from fastapi import APIRouter, HTTPException

from database.connection import get_connection
from schemas.auth_schema import LoginSchema
from utils.jwt_handler import crear_token

router = APIRouter()


@router.post("/auth/login")
def login(data: LoginSchema):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT
                id_usuario,
                nombre,
                email,
                password_hash,
                rol
            FROM usuarios_backoffice
            WHERE email = %s
              AND activo = true
        """
        cursor.execute(query, (data.email,))
        usuario = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado",
        )

    password_correcta = bcrypt.checkpw(
        data.password.encode(),
        usuario[3].encode(),
    )

    if not password_correcta:
        raise HTTPException(
            status_code=401,
            detail="Contrasena incorrecta",
        )

    datos_usuario = {
        "id_usuario": usuario[0],
        "nombre": usuario[1],
        "email": usuario[2],
        "rol": usuario[4],
    }

    return {
        "success": True,
        "token": crear_token(datos_usuario),
        "usuario": datos_usuario,
    }
