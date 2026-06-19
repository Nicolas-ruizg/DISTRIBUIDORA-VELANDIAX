from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from database.connection import get_db
from database.models import Cliente, ItemPedido, Pedido, VarianteProducto
from routes.admin import verificar_admin
from schemas.pedido import (
    PedidoCreate,
    PedidoDetalleResponse,
    PedidoResumenResponse,
    PedidoUpdate,
)

router = APIRouter(prefix="/admin/pedidos", tags=["pedidos"])


def _serializar_pedido_resumen(pedido: Pedido):
    return {
        "id_pedido": pedido.id_pedido,
        "id_cliente": pedido.id_cliente,
        "cliente": pedido.cliente.nombre,
        "celular": pedido.cliente.celular,
        "estado": pedido.estado,
        "total": pedido.total,
        "precio_envio": pedido.precio_envio,
        "es_mayorista": pedido.es_mayorista,
        "fecha": pedido.fecha,
        "items": len(pedido.items),
    }


def _serializar_item(item: ItemPedido):
    return {
        "id_item_pedido": item.id_item_pedido,
        "id_variante": item.id_variante,
        "id_producto": item.variante.id_producto,
        "producto": item.variante.producto.nombre,
        "cantidad": item.cantidad,
        "precio_unitario": item.precio_unitario,
        "atributos": item.variante.atributos or {},
    }


def _consulta_pedidos():
    return select(Pedido).options(
        joinedload(Pedido.cliente),
        selectinload(Pedido.items)
        .joinedload(ItemPedido.variante)
        .joinedload(VarianteProducto.producto),
    )


def _consultar_pedido(db: Session, id_pedido: int) -> Pedido:
    pedido = db.scalar(_consulta_pedidos().where(Pedido.id_pedido == id_pedido))
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado",
        )
    return pedido


def _serializar_pedido_detalle(pedido: Pedido):
    resumen = _serializar_pedido_resumen(pedido)
    items = sorted(pedido.items, key=lambda item: item.id_item_pedido)
    return {**resumen, "items_detalle": [_serializar_item(item) for item in items]}


def _obtener_o_crear_cliente(db: Session, pedido: PedidoCreate) -> Cliente:
    if pedido.id_cliente is not None:
        cliente = db.get(Cliente, pedido.id_cliente)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return cliente

    if pedido.cliente is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar id_cliente o datos del cliente",
        )

    cliente_existente = None
    if pedido.cliente.celular:
        cliente_existente = db.scalar(
            select(Cliente).where(Cliente.celular == pedido.cliente.celular)
        )
    if cliente_existente:
        cliente_existente.nombre = pedido.cliente.nombre
        return cliente_existente

    cliente = Cliente(
        nombre=pedido.cliente.nombre,
        celular=pedido.cliente.celular,
    )
    db.add(cliente)
    db.flush()
    return cliente


def _precio_item(variante: VarianteProducto, pedido_item, es_mayorista: bool) -> Decimal:
    if pedido_item.precio_unitario is not None:
        return pedido_item.precio_unitario
    return variante.precio_mayorista if es_mayorista else variante.precio_minorista


def _consultar_variantes_activas(db: Session, ids_variantes: set[int]):
    variantes = db.scalars(
        select(VarianteProducto)
        .options(joinedload(VarianteProducto.producto))
        .where(VarianteProducto.id_variante.in_(ids_variantes))
    ).all()
    variantes_por_id = {variante.id_variante: variante for variante in variantes}

    faltantes = ids_variantes - set(variantes_por_id)
    if faltantes:
        raise HTTPException(
            status_code=404,
            detail=f"Variantes no encontradas: {sorted(faltantes)}",
        )

    inactivas = [
        variante.id_variante
        for variante in variantes
        if variante.estado != "ACTIVO" or variante.producto.estado != "ACTIVO"
    ]
    if inactivas:
        raise HTTPException(
            status_code=400,
            detail=f"Variantes inactivas o con producto inactivo: {sorted(inactivas)}",
        )

    return variantes_por_id


@router.get("", response_model=list[PedidoResumenResponse])
def listar_pedidos(
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    pedidos = db.scalars(
        _consulta_pedidos().order_by(Pedido.fecha.desc(), Pedido.id_pedido.desc())
    ).all()
    return [_serializar_pedido_resumen(pedido) for pedido in pedidos]


@router.post("", response_model=PedidoDetalleResponse, status_code=status.HTTP_201_CREATED)
def crear_pedido(
    pedido: PedidoCreate,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    ids_variantes = {item.id_variante for item in pedido.items}
    variantes_por_id = _consultar_variantes_activas(db, ids_variantes)
    cliente = _obtener_o_crear_cliente(db, pedido)

    total_items = Decimal("0")
    pedido_db = Pedido(
        id_cliente=cliente.id_cliente,
        estado=pedido.estado,
        precio_envio=pedido.precio_envio,
        es_mayorista=pedido.es_mayorista,
        total=Decimal("0"),
    )
    db.add(pedido_db)
    db.flush()

    for item in pedido.items:
        variante = variantes_por_id[item.id_variante]
        precio_unitario = _precio_item(variante, item, pedido.es_mayorista)
        total_items += precio_unitario * item.cantidad
        db.add(
            ItemPedido(
                id_pedido=pedido_db.id_pedido,
                id_variante=item.id_variante,
                cantidad=item.cantidad,
                precio_unitario=precio_unitario,
            )
        )

    pedido_db.total = pedido.total if pedido.total is not None else total_items + pedido.precio_envio

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No fue posible crear el pedido",
        ) from exc

    return _serializar_pedido_detalle(_consultar_pedido(db, pedido_db.id_pedido))


@router.get("/{id_pedido}", response_model=PedidoDetalleResponse)
def obtener_pedido(
    id_pedido: int,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    return _serializar_pedido_detalle(_consultar_pedido(db, id_pedido))


@router.put("/{id_pedido}", response_model=PedidoDetalleResponse)
def actualizar_pedido(
    id_pedido: int,
    pedido: PedidoUpdate,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    cambios = pedido.model_dump(exclude_none=True)
    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )

    pedido_db = db.get(Pedido, id_pedido)
    if not pedido_db:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    for campo, valor in cambios.items():
        setattr(pedido_db, campo, valor)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="No fue posible actualizar el pedido") from exc
    return _serializar_pedido_detalle(_consultar_pedido(db, id_pedido))


@router.delete("/{id_pedido}", response_model=dict)
def eliminar_pedido(
    id_pedido: int,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    pedido_db = db.get(Pedido, id_pedido)
    if not pedido_db:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    db.delete(pedido_db)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="No fue posible eliminar el pedido") from exc
    return {"success": True, "id_pedido": id_pedido}
