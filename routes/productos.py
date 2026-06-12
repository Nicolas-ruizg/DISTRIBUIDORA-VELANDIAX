from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2.extras import Json

from database.connection import get_connection
from routes.admin import verificar_admin
from schemas.producto import (
    ProductoCreate,
    ProductoDetalleResponse,
    ProductoResumenResponse,
    ProductoUpdate,
    VarianteCreate,
    VarianteProductoResponse,
    VarianteUpdate,
)

router = APIRouter(tags=["productos"])


def _serializar_producto_resumen(fila):
    return {
        "id_producto": fila[0],
        "id_categoria": fila[1],
        "categoria": fila[2],
        "nombre": fila[3],
        "descripcion": fila[4],
        "paquete_estatico": fila[5],
        "variantes": fila[6],
        "precio_desde": fila[7],
    }


def _serializar_variante(fila):
    return {
        "id_variante": fila[0],
        "precio_costo": fila[1],
        "precio_minorista": fila[2],
        "precio_mayorista": fila[3],
        "peso": fila[4],
        "aplica_paquete": fila[5],
        "atributos": fila[6] or {},
    }


@router.get("/productos", response_model=list[ProductoResumenResponse])
@router.get("/admin/productos", response_model=list[ProductoResumenResponse])
def listar_productos(
    id_categoria: int | None = None,
    incluir_paquetes: bool = True,
):
    filtros = []
    parametros = []

    if id_categoria is not None:
        filtros.append("p.id_categoria = %s")
        parametros.append(id_categoria)

    if not incluir_paquetes:
        filtros.append("p.paquete_estatico = false")

    where = f"WHERE {' AND '.join(filtros)}" if filtros else ""

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            f"""
            SELECT
                p.id_producto,
                p.id_categoria,
                c.nombre AS categoria,
                p.nombre,
                p.descripcion,
                p.paquete_estatico,
                COUNT(v.id_variante) AS variantes,
                MIN(v.precio_minorista) AS precio_desde
            FROM producto p
            JOIN categoria c ON c.id_categoria = p.id_categoria
            LEFT JOIN variantes_producto v ON v.id_producto = p.id_producto
            {where}
            GROUP BY p.id_producto, p.id_categoria, c.nombre, p.nombre, p.descripcion, p.paquete_estatico
            ORDER BY p.nombre
            """,
            parametros,
        )
        return [_serializar_producto_resumen(fila) for fila in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()


@router.get("/productos/{id_producto}", response_model=ProductoDetalleResponse)
@router.get("/admin/productos/{id_producto}", response_model=ProductoDetalleResponse)
def obtener_producto(id_producto: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT
                p.id_producto,
                p.id_categoria,
                c.nombre AS categoria,
                p.nombre,
                p.descripcion,
                p.paquete_estatico
            FROM producto p
            JOIN categoria c ON c.id_categoria = p.id_categoria
            WHERE p.id_producto = %s
            """,
            (id_producto,),
        )
        producto = cursor.fetchone()

        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado",
            )

        cursor.execute(
            """
            SELECT
                id_variante,
                precio_costo,
                precio_minorista,
                precio_mayorista,
                peso,
                aplica_paquete,
                atributos
            FROM variantes_producto
            WHERE id_producto = %s
            ORDER BY id_variante
            """,
            (id_producto,),
        )
        variantes = [_serializar_variante(fila) for fila in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()

    return {
        "id_producto": producto[0],
        "id_categoria": producto[1],
        "categoria": producto[2],
        "nombre": producto[3],
        "descripcion": producto[4],
        "paquete_estatico": producto[5],
        "variantes": variantes,
    }


@router.post(
    "/admin/productos",
    response_model=ProductoDetalleResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_producto(
    producto: ProductoCreate,
    usuario: dict = Depends(verificar_admin),
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO producto (id_categoria, nombre, descripcion, paquete_estatico)
            VALUES (%s, %s, %s, %s)
            RETURNING id_producto
            """,
            (
                producto.id_categoria,
                producto.nombre,
                producto.descripcion,
                producto.paquete_estatico,
            ),
        )
        id_producto = cursor.fetchone()[0]
        conn.commit()
    except Exception as exc:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No fue posible crear el producto: {exc}",
        ) from exc
    finally:
        cursor.close()
        conn.close()

    return obtener_producto(id_producto)


@router.put("/admin/productos/{id_producto}", response_model=ProductoDetalleResponse)
def actualizar_producto(
    id_producto: int,
    producto: ProductoUpdate,
    usuario: dict = Depends(verificar_admin),
):
    cambios = producto.model_dump(exclude_none=True)
    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )

    asignaciones = [f"{campo} = %s" for campo in cambios]
    parametros = [*cambios.values(), id_producto]
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            f"""
            UPDATE producto
            SET {", ".join(asignaciones)}
            WHERE id_producto = %s
            RETURNING id_producto
            """,
            parametros,
        )
        fila = cursor.fetchone()
        if not fila:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado",
            )

        conn.commit()
    except HTTPException:
        conn.rollback()
        raise
    except Exception as exc:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No fue posible actualizar el producto: {exc}",
        ) from exc
    finally:
        cursor.close()
        conn.close()

    return obtener_producto(id_producto)


@router.delete("/admin/productos/{id_producto}", response_model=dict)
def eliminar_producto(
    id_producto: int,
    usuario: dict = Depends(verificar_admin),
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            DELETE FROM producto
            WHERE id_producto = %s
            RETURNING id_producto
            """,
            (id_producto,),
        )
        fila = cursor.fetchone()
        if not fila:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado",
            )

        conn.commit()
        return {"success": True, "id_producto": fila[0]}
    except HTTPException:
        conn.rollback()
        raise
    except Exception as exc:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No fue posible eliminar el producto: {exc}",
        ) from exc
    finally:
        cursor.close()
        conn.close()


@router.post(
    "/admin/productos/{id_producto}/variantes",
    response_model=VarianteProductoResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_variante(
    id_producto: int,
    variante: VarianteCreate,
    usuario: dict = Depends(verificar_admin),
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO variantes_producto (
                id_producto,
                precio_costo,
                precio_minorista,
                precio_mayorista,
                peso,
                aplica_paquete,
                atributos
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id_variante, precio_costo, precio_minorista, precio_mayorista,
                      peso, aplica_paquete, atributos
            """,
            (
                id_producto,
                variante.precio_costo,
                variante.precio_minorista,
                variante.precio_mayorista,
                variante.peso,
                variante.aplica_paquete,
                Json(variante.atributos),
            ),
        )
        creada = _serializar_variante(cursor.fetchone())
        conn.commit()
        return creada
    except Exception as exc:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No fue posible crear la variante: {exc}",
        ) from exc
    finally:
        cursor.close()
        conn.close()


@router.put("/admin/variantes/{id_variante}", response_model=VarianteProductoResponse)
def actualizar_variante(
    id_variante: int,
    variante: VarianteUpdate,
    usuario: dict = Depends(verificar_admin),
):
    cambios = variante.model_dump(exclude_none=True)
    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )

    parametros = []
    asignaciones = []
    for campo, valor in cambios.items():
        asignaciones.append(f"{campo} = %s")
        parametros.append(Json(valor) if campo == "atributos" else valor)
    parametros.append(id_variante)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            f"""
            UPDATE variantes_producto
            SET {", ".join(asignaciones)}
            WHERE id_variante = %s
            RETURNING id_variante, precio_costo, precio_minorista, precio_mayorista,
                      peso, aplica_paquete, atributos
            """,
            parametros,
        )
        fila = cursor.fetchone()
        if not fila:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Variante no encontrada",
            )

        actualizada = _serializar_variante(fila)
        conn.commit()
        return actualizada
    except HTTPException:
        conn.rollback()
        raise
    except Exception as exc:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No fue posible actualizar la variante: {exc}",
        ) from exc
    finally:
        cursor.close()
        conn.close()


@router.delete("/admin/variantes/{id_variante}", response_model=dict)
def eliminar_variante(
    id_variante: int,
    usuario: dict = Depends(verificar_admin),
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            DELETE FROM variantes_producto
            WHERE id_variante = %s
            RETURNING id_variante
            """,
            (id_variante,),
        )
        fila = cursor.fetchone()
        if not fila:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Variante no encontrada",
            )

        conn.commit()
        return {"success": True, "id_variante": fila[0]}
    except HTTPException:
        conn.rollback()
        raise
    except Exception as exc:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No fue posible eliminar la variante: {exc}",
        ) from exc
    finally:
        cursor.close()
        conn.close()
