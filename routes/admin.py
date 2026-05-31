import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database.connection import get_connection
from schemas.venta_schema import VentaCreate
from utils.calculadora_venta import calculadora
from utils.jwt_handler import verificar_token

router = APIRouter()
security = HTTPBearer()


def es_rol_admin(rol) -> bool:
    if rol == 1:
        return True

    return str(rol).strip().upper() in {"ADMIN", "ADMINISTRADOR"}


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
    return {
        "success": True,
        "mensaje": f"Bienvenido {usuario['nombre']}",
        "usuario": usuario,
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/admin/ventas", response_model=dict)
def crear_venta(
    venta_data: VentaCreate,
    usuario: dict = Depends(verificar_admin),
):
    es_valido, mensaje_validacion = calculadora.validar_productos(
        venta_data.productos
    )
    if not es_valido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validacion de productos fallo: {mensaje_validacion}",
        )

    totales = calculadora.calcular_totales(
        venta_data.productos,
        venta_data.impuesto_porcentaje,
    )
    fecha_creacion = datetime.now()
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # numero_venta es NOT NULL, por eso se reserva primero el ID serial.
        cursor.execute("SELECT nextval(pg_get_serial_sequence('ventas', 'id_venta'))")
        id_venta = cursor.fetchone()[0]
        numero_venta = calculadora.generar_numero_venta(id_venta)

        query_venta = """
            INSERT INTO ventas (
                id_venta,
                numero_venta,
                id_usuario_admin,
                nombre_cliente,
                email_cliente,
                telefono_cliente,
                empresa_cliente,
                forma_pago,
                subtotal,
                descuento_total,
                impuesto,
                impuesto_porcentaje,
                total,
                estado,
                referencia_externa,
                notas,
                fecha_creacion,
                productos_json
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        cursor.execute(
            query_venta,
            (
                id_venta,
                numero_venta,
                usuario.get("id_usuario"),
                venta_data.cliente.nombre,
                venta_data.cliente.email,
                venta_data.cliente.telefono,
                venta_data.cliente.empresa,
                venta_data.forma_pago.value,
                totales["subtotal"],
                totales["descuento_total"],
                totales["impuesto"],
                venta_data.impuesto_porcentaje,
                totales["total"],
                "confirmada",
                venta_data.referencia_externa,
                venta_data.notas,
                fecha_creacion,
                json.dumps(
                    [
                        producto.model_dump(mode="json")
                        for producto in venta_data.productos
                    ]
                ),
            ),
        )

        query_detalle = """
            INSERT INTO detalles_ventas (
                id_venta,
                id_producto,
                nombre_producto,
                cantidad,
                precio_unitario,
                descuento_porcentaje,
                subtotal_linea
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        for producto in venta_data.productos:
            cursor.execute(
                query_detalle,
                (
                    id_venta,
                    producto.id_producto,
                    producto.nombre_producto,
                    producto.cantidad,
                    producto.precio_unitario,
                    producto.descuento_porcentaje,
                    calculadora.calcular_subtotal_linea(producto),
                ),
            )

        conn.commit()
    except Exception as exc:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar venta: {exc}",
        ) from exc
    finally:
        cursor.close()
        conn.close()

    return {
        "success": True,
        "mensaje": "Venta registrada exitosamente",
        "venta": {
            "id_venta": id_venta,
            "numero_venta": numero_venta,
            "cliente": venta_data.cliente.model_dump(mode="json"),
            "productos": [
                producto.model_dump(mode="json") for producto in venta_data.productos
            ],
            "forma_pago": venta_data.forma_pago.value,
            "estado": "confirmada",
            "subtotal": totales["subtotal"],
            "descuento_total": totales["descuento_total"],
            "impuesto": totales["impuesto"],
            "impuesto_porcentaje": venta_data.impuesto_porcentaje,
            "total": totales["total"],
            "fecha_creacion": fecha_creacion.isoformat(),
            "vendedor": usuario.get("nombre"),
            "referencia_externa": venta_data.referencia_externa,
        },
    }

