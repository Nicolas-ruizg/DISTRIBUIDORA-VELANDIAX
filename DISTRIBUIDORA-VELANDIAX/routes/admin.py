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


def es_rol_admin(rol) -> bool:
    return str(rol).strip().upper() in {"1", "ADMIN", "ADMINISTRADOR"}


def verificar_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    usuario = verificar_token(credentials.credentials)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
        )

    if not es_rol_admin(usuario.get("rol")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores pueden realizar esta accion",
        )

    return usuario


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
