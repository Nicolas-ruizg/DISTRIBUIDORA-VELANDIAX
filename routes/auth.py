from fastapi import APIRouter, HTTPException
from schemas.auth_schema import LoginSchema
from database.connection import get_connection

import bcrypt
import jwt
import os

router = APIRouter()

@router.post("/auth/login")
def login(data: LoginSchema):

    conn = get_connection()

    cursor = conn.cursor()

    query = """
        SELECT 
            id_usuario,
            nombre,
            email,
            password_hash,
            rol
        FROM usuarios_backoffice
        WHERE email = %s
    """

    cursor.execute(query, (data.email,))

    usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    if not usuario:

        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    password_hash = usuario[3]

    password_correcta = bcrypt.checkpw(
        data.password.encode(),
        password_hash.encode()
    )

    if not password_correcta:

        raise HTTPException(
            status_code=401,
            detail="Contraseña incorrecta"
        )

    token = jwt.encode(
        {
            "id_usuario": usuario[0],
            "nombre": usuario[1],
            "rol": usuario[4]
        },
        os.getenv("JWT_SECRET"),
        algorithm="HS256"
    )

    return {
        "success": True,
        "token": token,
        "usuario": {
            "id_usuario": usuario[0],
            "nombre": usuario[1],
            "email": usuario[2],
            "rol": usuario[4]
        }
    }