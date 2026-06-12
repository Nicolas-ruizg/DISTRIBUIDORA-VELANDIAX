from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database.connection import get_connection
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
def dashboard(usuario: dict = Depends(verificar_admin)):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM clientes")
        total_clientes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM producto")
        total_productos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM variantes_producto")
        total_variantes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM pedido")
        total_pedidos = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(total), 0) FROM pedido")
        total_vendido = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT p.id_pedido, c.nombre, p.estado, p.total, p.fecha
            FROM pedido p
            JOIN clientes c ON c.id_cliente = p.id_cliente
            ORDER BY p.fecha DESC, p.id_pedido DESC
            LIMIT 5
            """
        )
        pedidos_recientes = [
            {
                "id_pedido": fila[0],
                "cliente": fila[1],
                "estado": fila[2],
                "total": fila[3],
                "fecha": fila[4],
            }
            for fila in cursor.fetchall()
        ]
    finally:
        cursor.close()
        conn.close()

    return {
        "success": True,
        "usuario": usuario,
        "metricas": {
            "clientes": total_clientes,
            "productos": total_productos,
            "variantes": total_variantes,
            "pedidos": total_pedidos,
            "total_vendido": total_vendido,
        },
        "pedidos_recientes": pedidos_recientes,
        "timestamp": datetime.now().isoformat(),
    }

