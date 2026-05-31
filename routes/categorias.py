from fastapi import APIRouter, Depends, HTTPException, status

from database.connection import get_connection
from routes.admin import verificar_admin
from schemas.categoria import CategoriaCreate, CategoriaResponse, CategoriaUpdate

router = APIRouter(prefix="/admin/categorias", tags=["categorias"])


def _serializar_categoria(fila):
    return {
        "id_categoria": fila[0],
        "nombre_categoria": fila[1],
        "activa": fila[2],
    }


@router.get("", response_model=list[CategoriaResponse])
def listar_categorias(usuario: dict = Depends(verificar_admin)):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id_categoria, nombre_categoria, activa
            FROM categorias
            ORDER BY nombre_categoria
            """
        )
        return [_serializar_categoria(fila) for fila in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()


@router.post(
    "",
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
            INSERT INTO categorias (nombre_categoria)
            VALUES (%s)
            RETURNING id_categoria, nombre_categoria, activa
            """,
            (categoria.nombre_categoria,),
        )
        categoria_creada = _serializar_categoria(cursor.fetchone())
        conn.commit()
        return categoria_creada
    except Exception as exc:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No fue posible crear la categoria: {exc}",
        ) from exc
    finally:
        cursor.close()
        conn.close()


@router.put("/{id_categoria}", response_model=CategoriaResponse)
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
            UPDATE categorias
            SET {", ".join(asignaciones)}
            WHERE id_categoria = %s
            RETURNING id_categoria, nombre_categoria, activa
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


@router.delete("/{id_categoria}", response_model=CategoriaResponse)
def desactivar_categoria(
    id_categoria: int,
    usuario: dict = Depends(verificar_admin),
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE categorias
            SET activa = false
            WHERE id_categoria = %s
            RETURNING id_categoria, nombre_categoria, activa
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
        return _serializar_categoria(fila)
    except HTTPException:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

