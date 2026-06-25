import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv()


def _obtener_configuracion_jwt():
    secret = os.getenv("JWT_SECRET")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")

    if not secret:
        raise RuntimeError("JWT_SECRET no esta configurado")

    return secret, algorithm


def crear_token(usuario):
    secret, algorithm = _obtener_configuracion_jwt()
    horas_expiracion = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

    if horas_expiracion <= 0:
        raise RuntimeError("JWT_EXPIRATION_HOURS debe ser mayor a cero")

    ahora = datetime.now(timezone.utc)
    payload = {
        "id_usuario": usuario["id_usuario"],
        "nombre": usuario["nombre"],
        "rol": usuario["rol"],
        "iat": ahora,
        "exp": ahora + timedelta(hours=horas_expiracion),
    }

    return jwt.encode(payload, secret, algorithm=algorithm)


def verificar_token(token):
    try:
        secret, algorithm = _obtener_configuracion_jwt()
        return jwt.decode(token, secret, algorithms=[algorithm])
    except (jwt.PyJWTError, RuntimeError, ValueError):
        return None
