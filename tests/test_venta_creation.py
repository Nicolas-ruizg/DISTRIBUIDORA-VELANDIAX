from datetime import datetime, timedelta, timezone
from decimal import Decimal

import jwt
import pytest
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import ValidationError

from routes import admin
from schemas.venta_schema import VentaCreate
from utils.calculadora_venta import calculadora
from utils.jwt_handler import crear_token, verificar_token


@pytest.fixture(autouse=True)
def configurar_jwt(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret-that-is-long-enough-for-local-tests")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_EXPIRATION_HOURS", "24")


def crear_payload_venta():
    return VentaCreate(
        cliente={
            "nombre": "Cliente Test",
            "email": "cliente@test.com",
        },
        productos=[
            {
                "id_producto": 1,
                "nombre_producto": "Producto Test",
                "cantidad": 2,
                "precio_unitario": 100,
                "descuento_porcentaje": 10,
            }
        ],
        forma_pago="efectivo",
    )


def test_calcular_totales_con_descuento_e_impuesto():
    productos = crear_payload_venta().productos

    assert calculadora.calcular_totales(productos, Decimal("19")) == {
        "subtotal": Decimal("200.00"),
        "descuento_total": Decimal("20.00"),
        "subtotal_con_descuento": Decimal("180.00"),
        "impuesto": Decimal("34.20"),
        "total": Decimal("214.20"),
    }


def test_generar_numero_venta_con_anio_indicado():
    assert calculadora.generar_numero_venta(42, 2030) == "VTA-2030-0000042"


def test_rechazar_venta_sin_productos():
    with pytest.raises(ValidationError):
        VentaCreate(
            cliente={"nombre": "Cliente Test", "email": "cliente@test.com"},
            productos=[],
            forma_pago="efectivo",
        )


def test_aceptar_rol_administrador_de_base_de_datos():
    token = crear_token(
        {"id_usuario": 1, "nombre": "Admin Test", "rol": "ADMINISTRADOR"}
    )
    credenciales = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    usuario = admin.verificar_admin(credenciales)

    assert usuario["rol"] == "ADMINISTRADOR"
    assert "exp" in usuario


def test_rechazar_token_expirado():
    token = jwt.encode(
        {
            "id_usuario": 1,
            "nombre": "Admin Test",
            "rol": "ADMINISTRADOR",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        "test-secret-that-is-long-enough-for-local-tests",
        algorithm="HS256",
    )

    assert verificar_token(token) is None


def test_crear_venta_inserta_numero_obligatorio_antes_del_detalle(monkeypatch):
    class CursorFalso:
        def __init__(self):
            self.consultas = []
            self.resultado = None

        def execute(self, query, params=None):
            self.consultas.append((" ".join(query.split()), params))
            if query.startswith("SELECT nextval"):
                self.resultado = (42,)

        def fetchone(self):
            return self.resultado

        def close(self):
            pass

    class ConexionFalsa:
        def __init__(self):
            self.cursor_falso = CursorFalso()
            self.confirmada = False

        def cursor(self):
            return self.cursor_falso

        def commit(self):
            self.confirmada = True

        def rollback(self):
            pass

        def close(self):
            pass

    conexion = ConexionFalsa()
    monkeypatch.setattr(admin, "get_connection", lambda: conexion)

    respuesta = admin.crear_venta(
        crear_payload_venta(),
        {"id_usuario": 1, "nombre": "Admin Test", "rol": "ADMINISTRADOR"},
    )

    consulta_venta, parametros = conexion.cursor_falso.consultas[1]
    numero_esperado = f"VTA-{datetime.now().year}-0000042"
    assert "INSERT INTO ventas ( id_venta, numero_venta," in consulta_venta
    assert parametros[:2] == (42, numero_esperado)
    assert conexion.confirmada is True
    assert respuesta["venta"]["numero_venta"] == numero_esperado

