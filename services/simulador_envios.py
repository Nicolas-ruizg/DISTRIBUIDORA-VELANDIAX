import asyncio
import logging
from datetime import datetime

from sqlalchemy import select

from database.connection import SessionLocal
from database.models import Envio


logger = logging.getLogger(__name__)

ESTADOS_ENVIO = (
    "PENDIENTE",
    "PREPARANDO",
    "DESPACHADO",
    "EN_TRANSITO",
    "ENTREGADO",
)


def siguiente_estado(estado_actual: str) -> str | None:
    try:
        posicion = ESTADOS_ENVIO.index(estado_actual)
    except ValueError:
        return None

    if posicion == len(ESTADOS_ENVIO) - 1:
        return None
    return ESTADOS_ENVIO[posicion + 1]


def avanzar_envios() -> int:
    db = SessionLocal()
    actualizados = 0
    try:
        envios = db.scalars(
            select(Envio).where(Envio.estado.in_(ESTADOS_ENVIO[:-1]))
        ).all()
        ahora = datetime.now()

        for envio in envios:
            nuevo_estado = siguiente_estado(envio.estado)
            if not nuevo_estado:
                continue

            envio.estado = nuevo_estado
            envio.pedido.estado = nuevo_estado
            if nuevo_estado == "DESPACHADO" and envio.fecha_despacho is None:
                envio.fecha_despacho = ahora
            if nuevo_estado == "ENTREGADO" and envio.fecha_entrega is None:
                envio.fecha_entrega = ahora
            actualizados += 1

        db.commit()
        return actualizados
    except Exception:
        db.rollback()
        logger.exception("No fue posible avanzar la simulacion de envios")
        return 0
    finally:
        db.close()


async def ejecutar_simulador(intervalo_segundos: int = 30):
    while True:
        await asyncio.sleep(intervalo_segundos)
        await asyncio.to_thread(avanzar_envios)
