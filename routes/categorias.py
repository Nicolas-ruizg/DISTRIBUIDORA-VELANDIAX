from fastapi import APIRouter, Depends, HTTPException, status

from database.connection import get_connection
from routes.admin import verificar_admin
from schemas.categoria import CategoriaCreate, CategoriaResponse, CategoriaUpdate

router = APIRouter(tags=["categorias"])


def _serializar_categoria(fila):
    return {
        "id_categoria": fila[0],
        "nombre": fila[1],
        "descripcion": fila[2],
    }


@router.get("/categorias", response_model=list[CategoriaResponse])
@router.get("/admin/categorias", response_model=list[CategoriaResponse])
def listar_categorias():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id_categoria, nombre, descripcion
            FROM categoria
            ORDER BY nombre
            """
        )
        return [_serializar_categoria(fila) for fila in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()


@router.get("/categorias/{id_categoria}", response_model=CategoriaResponse)
@router.get("/admin/categorias/{id_categoria}", response_model=CategoriaResponse)
def obtener_categoria(id_categoria: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id_categoria, nombre, descripcion
            FROM categoria
            WHERE id_categoria = %s
            """,
            (id_categoria,),
        )
        fila = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not fila:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria no encontrada",
        )

    return _serializar_categoria(fila)


@router.post(
    "/admin/categorias",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_categoria(
    categoria: CategoriaCreate,
    usuario: dict = Depends(verificar_admin),
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO categoria (nombre, descripcion)
            VALUES (%s, %s)
            RETURNING id_categoria, nombre, descripcion
            """,
            (categoria.nombre, categoria.descripcion),
        )
        creada = _serializar_categoria(cursor.fetchone())
        conn.commit()
        return creada
    except Exception as exc:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No fue posible crear la categoria: {exc}",
        ) from exc
    finally:
        cursor.close()
        conn.close()


@router.put("/admin/categorias/{id_categoria}", response_model=CategoriaResponse)
def actualizar_categoria(
    id_categoria: int,
    categoria: CategoriaUpdate,
    usuario: dict = Depends(verificar_admin),
):
    cambios = categoria.model_dump(exclude_none=True)
    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )

    asignaciones = [f"{campo} = %s" for campo in cambios]
    parametros = [*cambios.values(), id_categoria]
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            f"""
            UPDATE categoria
            SET {", ".join(asignaciones)}
            WHERE id_categoria = %s
            RETURNING id_categoria, nombre, descripcion
            """,
            parametros,
        )
        fila = cursor.fetchone()
        if not fila:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria no encontrada",
            )

        conn.commit()
        return _serializar_categoria(fila)
    except HTTPException:
        conn.rollback()
        raise
    except Exception as exc:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No fue posible actualizar la categoria: {exc}",
        ) from exc
    finally:
        cursor.close()
        conn.close()


@router.delete("/admin/categorias/{id_categoria}", response_model=dict)
def eliminar_categoria(
    id_categoria: int,
    usuario: dict = Depends(verificar_admin),
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            DELETE FROM categoria
            WHERE id_categoria = %s
            RETURNING id_categoria
            """,
            (id_categoria,),
        )
        fila = cursor.fetchone()
        if not fila:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria no encontrada",
            )

        conn.commit()
        return {"success": True, "id_categoria": fila[0]}
    except HTTPException:
        conn.rollback()
        raise
    except Exception as exc:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No fue posible eliminar la categoria: {exc}",
        ) from exc
    finally:
        cursor.close()
        conn.close()
