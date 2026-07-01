from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from database.connection import get_db
from database.models import Cliente, Pedido, Producto, VarianteProducto
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
    usuario: dict = Depends(verificar_admin),
    db: Session = Depends(get_db),
):
    pedidos = db.scalars(
        select(Pedido)
        .options(joinedload(Pedido.cliente))
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
            "pedidos": db.scalar(select(func.count()).select_from(Pedido)),
            "total_vendido": db.scalar(
                select(func.coalesce(func.sum(Pedido.total), 0))
            ),
        },
        "pedidos_recientes": [
            {
                "id_pedido": pedido.id_pedido,
                "cliente": pedido.cliente.nombre,
                "estado": pedido.estado,
                "total": pedido.total,
                "fecha": pedido.fecha,
            }
            for pedido in pedidos
        ],
        "timestamp": datetime.now().isoformat(),
    }
