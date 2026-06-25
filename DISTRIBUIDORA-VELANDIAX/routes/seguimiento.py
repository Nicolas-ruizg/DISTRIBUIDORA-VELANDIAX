from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from database.connection import get_db
from database.models import Cliente, Envio, ItemPedido, Pedido
from schemas.pedido import PedidoSeguimientoResponse


router = APIRouter(tags=["seguimiento"])

ESTADOS_FINALES = {"ENTREGADO", "CANCELADO", "COMPLETADO", "REEMBOLSADO"}


def _limpiar_celular(celular: str) -> str:
    return "".join(caracter for caracter in celular if caracter.isdigit())


@router.get("/pedidos/seguimiento", response_model=list[PedidoSeguimientoResponse])
def consultar_pedidos_por_celular(
    celular: str = Query(min_length=7, max_length=20),
    db: Session = Depends(get_db),
):
    celular_limpio = _limpiar_celular(celular)

    pedidos = db.scalars(
        select(Pedido)
        .join(Cliente)
        .options(
            joinedload(Pedido.envio),
            selectinload(Pedido.items).joinedload(ItemPedido.variante),
        )
        .where(Cliente.celular == celular_limpio)
        .order_by(Pedido.fecha.desc(), Pedido.id_pedido.desc())
    ).all()

    pedidos_activos = []
    for pedido in pedidos:
        estado_pedido = (pedido.estado or "").upper()
        estado_envio = (pedido.envio.estado if pedido.envio else "") or ""
        if estado_pedido in ESTADOS_FINALES or estado_envio.upper() in ESTADOS_FINALES:
            continue

        pedidos_activos.append(
            {
                "id_pedido": pedido.id_pedido,
                "estado": pedido.estado,
                "estado_pago": pedido.estado_pago,
                "numero_guia": pedido.envio.numero_guia if pedido.envio else None,
                "estado_envio": pedido.envio.estado if pedido.envio else None,
                "transportadora": pedido.envio.transportadora if pedido.envio else None,
                "total": pedido.total,
                "fecha": pedido.fecha,
                "items": len(pedido.items),
            }
        )

    return pedidos_activos
