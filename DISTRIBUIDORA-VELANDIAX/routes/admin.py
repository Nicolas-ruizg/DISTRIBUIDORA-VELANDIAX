from datetime import date, datetime, time

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from database.connection import get_db
from database.models import Cliente, Deposito, ItemPedido, Pedido, Producto, Usuario, VarianteProducto
from utils.jwt_handler import verificar_token

router = APIRouter()
security = HTTPBearer()

ROL_ADMIN = "ADMINISTRADOR"
ROL_VENDEDOR = "VENDEDOR"
ROL_INVENTARIO = "INVENTARIO"
ROLES_VALIDOS = {ROL_ADMIN, ROL_VENDEDOR, ROL_INVENTARIO}


def normalizar_rol(rol) -> str:
    return str(rol or "").strip().upper()


def verificar_usuario_autenticado(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    usuario = verificar_token(credentials.credentials)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
        )

    return usuario


def requerir_roles(*roles_permitidos: str):
    roles = {normalizar_rol(rol) for rol in roles_permitidos}

    def _verificar(usuario: dict = Depends(verificar_usuario_autenticado)):
        if normalizar_rol(usuario.get("rol")) not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado para este rol",
            )
        return usuario

    return _verificar


verificar_admin = requerir_roles(ROL_ADMIN)
verificar_inventario = requerir_roles(ROL_ADMIN, ROL_INVENTARIO)
verificar_ventas = requerir_roles(ROL_ADMIN, ROL_VENDEDOR)


@router.get("/admin/dashboard")
def dashboard(
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    id_usuario_venta: int | None = None,
    id_deposito: str | None = None,
    referencia: str | None = None,
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    filtros_pedido = []
    if fecha_desde:
        filtros_pedido.append(Pedido.fecha >= datetime.combine(fecha_desde, time.min))
    if fecha_hasta:
        filtros_pedido.append(Pedido.fecha <= datetime.combine(fecha_hasta, time.max))
    if id_usuario_venta:
        filtros_pedido.append(Pedido.id_usuario_venta == id_usuario_venta)
    if id_deposito:
        filtros_pedido.append(Pedido.id_deposito == id_deposito.strip().upper())
    if referencia:
        patron = f"%{referencia.strip()}%"
        filtros_pedido.append(
            Pedido.items.any(
                ItemPedido.variante.has(
                    VarianteProducto.producto.has(
                        or_(
                            Producto.codigo_producto.ilike(patron),
                            Producto.nombre.ilike(patron),
                        )
                    )
                )
            )
        )

    consulta_pedidos = select(Pedido).where(*filtros_pedido)
    pedidos = db.scalars(
        consulta_pedidos
        .options(joinedload(Pedido.cliente))
        .options(joinedload(Pedido.deposito))
        .options(joinedload(Pedido.usuario_venta))
        .order_by(Pedido.fecha.desc(), Pedido.id_pedido.desc())
        .limit(5)
    ).all()
    return {
        "success": True,
        "usuario": usuario,
        "metricas": {
            "clientes": db.scalar(select(func.count()).select_from(Cliente)),
            "productos": db.scalar(select(func.count()).select_from(Producto)),
            "variantes": db.scalar(select(func.count()).select_from(VarianteProducto)),
            "pedidos": db.scalar(
                select(func.count()).select_from(Pedido).where(*filtros_pedido)
            ),
            "total_vendido": db.scalar(
                select(func.coalesce(func.sum(Pedido.total), 0)).where(*filtros_pedido)
            ),
        },
        "filtros": {
            "fecha_desde": fecha_desde.isoformat() if fecha_desde else None,
            "fecha_hasta": fecha_hasta.isoformat() if fecha_hasta else None,
            "id_usuario_venta": id_usuario_venta,
            "id_deposito": id_deposito.strip().upper() if id_deposito else None,
            "referencia": referencia.strip() if referencia else None,
        },
        "opciones": {
            "vendedores": [
                {
                    "id_usuario": vendedor.id_usuario,
                    "nombre": vendedor.nombre,
                    "codigo_cuenta": vendedor.codigo_cuenta,
                }
                for vendedor in db.scalars(
                    select(Usuario)
                    .where(Usuario.rol.in_(["VENDEDOR", "ADMINISTRADOR"]), Usuario.activo.is_(True))
                    .order_by(Usuario.nombre)
                ).all()
            ],
            "depositos": [
                {
                    "id_deposito": deposito.id_deposito,
                    "nombre": deposito.nombre,
                }
                for deposito in db.scalars(
                    select(Deposito).where(Deposito.activo.is_(True)).order_by(Deposito.id_deposito)
                ).all()
            ],
            "referencias": [
                {
                    "codigo_producto": producto.codigo_producto,
                    "nombre": producto.nombre,
                }
                for producto in db.scalars(
                    select(Producto).order_by(Producto.codigo_producto).limit(200)
                ).all()
            ],
        },
        "pedidos_recientes": [
            {
                "id_pedido": pedido.id_pedido,
                "cliente": pedido.cliente.nombre,
                "deposito": pedido.deposito.nombre if pedido.deposito else pedido.id_deposito,
                "vendedor": pedido.usuario_venta.nombre if pedido.usuario_venta else None,
                "estado": pedido.estado,
                "total": pedido.total,
                "fecha": pedido.fecha,
            }
            for pedido in pedidos
        ],
        "timestamp": datetime.now().isoformat(),
    }
