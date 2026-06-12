from fastapi import APIRouter, Depends, HTTPException, status

from database.connection import get_connection
from routes.admin import verificar_admin
from schemas.pedido import PedidoDetalleResponse, PedidoResumenResponse, PedidoUpdate

router = APIRouter(prefix="/admin/pedidos", tags=["pedidos"])


def _serializar_pedido_resumen(fila):
    return {
        "id_pedido": fila[0],
        "id_cliente": fila[1],
        "cliente": fila[2],
        "celular": fila[3],
        "estado": fila[4],
        "total": fila[5],
        "precio_envio": fila[6],
        "es_mayorista": fila[7],
        "fecha": fila[8],
        "items": fila[9],
    }


def _serializar_item(fila):
    return {
        "id_item_pedido": fila[0],
        "id_variante": fila[1],
        "id_producto": fila[2],
        "producto": fila[3],
        "cantidad": fila[4],
        "precio_unitario": fila[5],
        "atributos": fila[6] or {},
    }


@router.get("", response_model=list[PedidoResumenResponse])
def listar_pedidos(usuario: dict = Depends(verificar_admin)):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT
                p.id_pedido,
                p.id_cliente,
                c.nombre AS cliente,
                c.celular,
                p.estado,
                p.total,
                p.precio_envio,
                p.es_mayorista,
                p.fecha,
                COUNT(i.id_item_pedido) AS items
            FROM pedido p
            JOIN clientes c ON c.id_cliente = p.id_cliente
            LEFT JOIN items_pedido i ON i.id_pedido = p.id_pedido
            GROUP BY p.id_pedido, p.id_cliente, c.nombre, c.celular, p.estado, p.total,
                     p.precio_envio, p.es_mayorista, p.fecha
            ORDER BY p.fecha DESC, p.id_pedido DESC
            """
        )
        return [_serializar_pedido_resumen(fila) for fila in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()


@router.get("/{id_pedido}", response_model=PedidoDetalleResponse)
def obtener_pedido(id_pedido: int, usuario: dict = Depends(verificar_admin)):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT
                p.id_pedido,
                p.id_cliente,
                c.nombre AS cliente,
                c.celular,
                p.estado,
                p.total,
                p.precio_envio,
                p.es_mayorista,
                p.fecha
            FROM pedido p
            JOIN clientes c ON c.id_cliente = p.id_cliente
            WHERE p.id_pedido = %s
            """,
            (id_pedido,),
        )
        pedido = cursor.fetchone()

        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )

        cursor.execute(
            """
            SELECT
                i.id_item_pedido,
                i.id_variante,
                v.id_producto,
                pr.nombre,
                i.cantidad,
                i.precio_unitario,
                v.atributos
            FROM items_pedido i
            JOIN variantes_producto v ON v.id_variante = i.id_variante
            JOIN producto pr ON pr.id_producto = v.id_producto
            WHERE i.id_pedido = %s
            ORDER BY i.id_item_pedido
            """,
            (id_pedido,),
        )
        items = [_serializar_item(fila) for fila in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()

    resumen = _serializar_pedido_resumen((*pedido, len(items)))
    return {**resumen, "items_detalle": items}


@router.put("/{id_pedido}", response_model=PedidoDetalleResponse)
def actualizar_pedido(
    id_pedido: int,
    pedido: PedidoUpdate,
    usuario: dict = Depends(verificar_admin),
):
    cambios = pedido.model_dump(exclude_none=True)
    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )

    asignaciones = [f"{campo} = %s" for campo in cambios]
    parametros = [*cambios.values(), id_pedido]
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            f"""
            UPDATE pedido
            SET {", ".join(asignaciones)}
            WHERE id_pedido = %s
            RETURNING id_pedido
            """,
            parametros,
        )
        fila = cursor.fetchone()
        if not fila:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )

        conn.commit()
    except HTTPException:
        conn.rollback()
        raise
    except Exception as exc:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No fue posible actualizar el pedido: {exc}",
        ) from exc
    finally:
        cursor.close()
        conn.close()

    return obtener_pedido(id_pedido, usuario)


@router.delete("/{id_pedido}", response_model=dict)
def eliminar_pedido(
    id_pedido: int,
    usuario: dict = Depends(verificar_admin),
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            DELETE FROM pedido
            WHERE id_pedido = %s
            RETURNING id_pedido
            """,
            (id_pedido,),
        )
        fila = cursor.fetchone()
        if not fila:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )

        conn.commit()
        return {"success": True, "id_pedido": fila[0]}
    except HTTPException:
        conn.rollback()
        raise
    except Exception as exc:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No fue posible eliminar el pedido: {exc}",
        ) from exc
    finally:
        cursor.close()
        conn.close()
