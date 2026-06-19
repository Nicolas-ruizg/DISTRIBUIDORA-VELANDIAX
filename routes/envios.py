from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from database.connection import get_db
from database.models import Envio, Pedido
from routes.admin import verificar_admin
from schemas.envio import EnvioCreate, EnvioResponse, SeguimientoEnvioResponse


router = APIRouter(tags=["envios"])


def _serializar_envio(envio: Envio):
    return {
        "id_envio": envio.id_envio,
        "id_pedido": envio.id_pedido,
        "transportadora": envio.transportadora,
        "numero_guia": envio.numero_guia,
        "estado": envio.estado,
        "nombre_destinatario": envio.nombre_destinatario,
        "celular_destinatario": envio.celular_destinatario,
        "direccion": envio.direccion,
        "ciudad": envio.ciudad,
        "departamento": envio.departamento,
        "codigo_postal": envio.codigo_postal,
        "notas": envio.notas,
        "costo": envio.costo,
        "fecha_despacho": envio.fecha_despacho,
        "fecha_entrega": envio.fecha_entrega,
        "fecha_creacion": envio.fecha_creacion,
    }


@router.post(
    "/admin/pedidos/{id_pedido}/envio",
    response_model=EnvioResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_envio(
    id_pedido: int,
    datos: EnvioCreate,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    pedido = db.scalar(
        select(Pedido)
        .options(joinedload(Pedido.envio))
        .where(Pedido.id_pedido == id_pedido)
    )
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if pedido.envio:
        raise HTTPException(status_code=409, detail="El pedido ya tiene un envio")

    envio = Envio(
        id_pedido=id_pedido,
        numero_guia=datos.numero_guia or f"VEL-{id_pedido}-{datetime.now():%Y%m%d%H%M%S}",
        estado="PENDIENTE",
        **datos.model_dump(exclude={"numero_guia"}),
    )
    pedido.estado = "PENDIENTE"
    pedido.precio_envio = datos.costo
    db.add(envio)

    try:
        db.commit()
        db.refresh(envio)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No fue posible crear el envio; verifique el numero de guia",
        ) from exc
    return _serializar_envio(envio)


@router.get("/admin/envios", response_model=list[EnvioResponse])
def listar_envios(
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    envios = db.scalars(select(Envio).order_by(Envio.fecha_creacion.desc())).all()
    return [_serializar_envio(envio) for envio in envios]


@router.get("/admin/pedidos/{id_pedido}/envio", response_model=EnvioResponse)
def obtener_envio_pedido(
    id_pedido: int,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    envio = db.scalar(select(Envio).where(Envio.id_pedido == id_pedido))
    if not envio:
        raise HTTPException(status_code=404, detail="Envio no encontrado")
    return _serializar_envio(envio)


@router.get(
    "/envios/seguimiento/{numero_guia}",
    response_model=SeguimientoEnvioResponse,
)
def consultar_seguimiento(numero_guia: str, db: Session = Depends(get_db)):
    envio = db.scalar(select(Envio).where(Envio.numero_guia == numero_guia))
    if not envio:
        raise HTTPException(status_code=404, detail="Numero de guia no encontrado")

    return {
        "numero_guia": envio.numero_guia,
        "transportadora": envio.transportadora,
        "estado": envio.estado,
        "ciudad": envio.ciudad,
        "fecha_despacho": envio.fecha_despacho,
        "fecha_entrega": envio.fecha_entrega,
        "fecha_creacion": envio.fecha_creacion,
    }
