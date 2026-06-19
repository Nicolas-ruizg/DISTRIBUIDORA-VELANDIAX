from datetime import datetime
from decimal import Decimal

import pytest
from fastapi import HTTPException

from database.models import (
    Categoria,
    Cliente,
    ImagenProducto,
    ImagenVarianteProducto,
    ItemPedido,
    Pedido,
    Producto,
    VarianteProducto,
)
from routes import categorias, pedidos, productos
from schemas.pedido import PedidoItemCreate
from schemas.producto import ProductoUpdate, VarianteUpdate


class ResultadoEscalarFalso:
    def __init__(self, objetos):
        self.objetos = objetos

    def all(self):
        return self.objetos


class SesionFalsa:
    def __init__(self, objetos=None, objeto=None):
        self.objetos = objetos or []
        self.objeto = objeto
        self.consultas = []
        self.commit_ejecutado = False

    def scalars(self, consulta):
        self.consultas.append(consulta)
        return ResultadoEscalarFalso(self.objetos)

    def scalar(self, consulta):
        self.consultas.append(consulta)
        return self.objeto

    def get(self, modelo, id_objeto):
        return self.objeto

    def commit(self):
        self.commit_ejecutado = True

    def refresh(self, objeto):
        pass


def crear_producto_prueba():
    categoria = Categoria(
        id_categoria=2,
        nombre="Ropa Deportiva",
        descripcion="Descripcion",
    )
    producto = Producto(
        id_producto=1,
        id_categoria=2,
        nombre="Camiseta",
        descripcion="Dry fit",
        paquete_estatico=False,
        estado="ACTIVO",
    )
    producto.categoria = categoria
    producto.imagenes = [
        ImagenProducto(
            id_imagen=1,
            id_producto=1,
            url="https://cdn.velandiax.com/camiseta-principal.jpg",
            alt_text="Camiseta principal",
            es_principal=True,
            orden=0,
            estado="ACTIVO",
        ),
        ImagenProducto(
            id_imagen=2,
            id_producto=1,
            url="https://cdn.velandiax.com/camiseta-inactiva.jpg",
            alt_text="Camiseta inactiva",
            es_principal=False,
            orden=1,
            estado="INACTIVO",
        ),
    ]
    variante_activa = VarianteProducto(
            id_variante=3,
            id_producto=1,
            precio_costo=Decimal("5"),
            precio_minorista=Decimal("12"),
            precio_mayorista=Decimal("8.5"),
            peso=Decimal("0.15"),
            aplica_paquete=True,
            atributos={"talla": "M"},
            estado="ACTIVO",
    )
    variante_activa.imagenes = [
        ImagenVarianteProducto(
            id_imagen_variante=1,
            id_variante=3,
            url="https://cdn.velandiax.com/variante-m.jpg",
            alt_text="Variante talla M",
            es_principal=True,
            orden=0,
            estado="ACTIVO",
        )
    ]
    variante_inactiva = VarianteProducto(
            id_variante=4,
            id_producto=1,
            precio_costo=Decimal("6"),
            precio_minorista=Decimal("15"),
            precio_mayorista=Decimal("10"),
            peso=None,
            aplica_paquete=False,
            atributos={},
            estado="INACTIVO",
    )
    variante_inactiva.imagenes = []
    producto.variantes = [variante_activa, variante_inactiva]
    return producto


def test_listar_categorias_con_sesion_sqlalchemy():
    categoria = Categoria(id_categoria=1, nombre="Ropa Deportiva", descripcion="Descripcion")
    db = SesionFalsa(objetos=[categoria])

    respuesta = categorias.listar_categorias(db)

    assert respuesta[0]["nombre"] == "Ropa Deportiva"
    assert "categoria" in str(db.consultas[0])


def test_listar_productos_incluye_precio_desde():
    db = SesionFalsa(objetos=[crear_producto_prueba()])

    respuesta = productos.listar_productos(db=db)

    assert respuesta[0]["nombre"] == "Camiseta"
    assert respuesta[0]["estado"] == "ACTIVO"
    assert respuesta[0]["variantes"] == 1
    assert respuesta[0]["precio_desde"] == Decimal("12")
    assert respuesta[0]["imagen_principal"] == "https://cdn.velandiax.com/camiseta-principal.jpg"


def test_obtener_producto_devuelve_atributos_json():
    db = SesionFalsa(objeto=crear_producto_prueba())

    respuesta = productos.obtener_producto(1, db)

    assert respuesta["id_producto"] == 1
    assert respuesta["estado"] == "ACTIVO"
    assert len(respuesta["imagenes"]) == 1
    assert respuesta["imagenes"][0]["url"] == "https://cdn.velandiax.com/camiseta-principal.jpg"
    assert len(respuesta["variantes"]) == 1
    assert respuesta["variantes"][0]["estado"] == "ACTIVO"
    assert respuesta["variantes"][0]["atributos"] == {"talla": "M"}
    assert respuesta["variantes"][0]["imagen_principal"] == "https://cdn.velandiax.com/variante-m.jpg"
    assert len(respuesta["variantes"][0]["imagenes"]) == 1


def test_actualizar_producto_lo_marca_inactivo():
    producto = crear_producto_prueba()
    db = SesionFalsa(objeto=producto)

    respuesta = productos.actualizar_producto(
        1,
        ProductoUpdate(estado="INACTIVO"),
        {"rol": "ADMINISTRADOR"},
        db,
    )

    assert respuesta["id_producto"] == 1
    assert respuesta["estado"] == "INACTIVO"
    assert producto.estado == "INACTIVO"
    assert db.commit_ejecutado is True


def test_actualizar_variante_lo_marca_inactivo():
    variante = crear_producto_prueba().variantes[0]
    db = SesionFalsa(objeto=variante)

    respuesta = productos.actualizar_variante(
        3,
        VarianteUpdate(estado="INACTIVO"),
        {"rol": "ADMINISTRADOR"},
        db,
    )

    assert respuesta["id_variante"] == 3
    assert respuesta["estado"] == "INACTIVO"
    assert variante.estado == "INACTIVO"
    assert db.commit_ejecutado is True


def test_listar_pedidos_carga_cliente_e_items():
    cliente = Cliente(id_cliente=1, nombre="Carlos", celular="+57300")
    pedido = Pedido(
        id_pedido=1,
        id_cliente=1,
        estado="Entregado",
        total=Decimal("47"),
        precio_envio=Decimal("5"),
        es_mayorista=False,
        fecha=datetime(2026, 6, 10),
    )
    pedido.cliente = cliente
    pedido.items = [ItemPedido(id_item_pedido=1, id_variante=3, cantidad=2, precio_unitario=Decimal("21"))]
    db = SesionFalsa(objetos=[pedido])

    respuesta = pedidos.listar_pedidos({"rol": "ADMINISTRADOR"}, db)

    assert respuesta[0]["cliente"] == "Carlos"
    assert respuesta[0]["items"] == 1
    assert "pedido" in str(db.consultas[0])


def test_precio_item_toma_tarifa_segun_tipo_cliente():
    variante = crear_producto_prueba().variantes[0]

    precio_minorista = pedidos._precio_item(
        variante,
        PedidoItemCreate(id_variante=3, cantidad=1),
        es_mayorista=False,
    )
    precio_mayorista = pedidos._precio_item(
        variante,
        PedidoItemCreate(id_variante=3, cantidad=1),
        es_mayorista=True,
    )

    assert precio_minorista == Decimal("12")
    assert precio_mayorista == Decimal("8.5")


def test_no_permite_crear_pedido_con_variante_inactiva():
    producto = crear_producto_prueba()
    db = SesionFalsa(objetos=[producto.variantes[1]])

    with pytest.raises(HTTPException) as error:
        pedidos._consultar_variantes_activas(db, {4})

    assert error.value.status_code == 400


def test_extension_imagen_permite_formatos_validos():
    assert productos._extension_imagen("image/png") == ".png"
    assert productos._extension_imagen("image/webp") == ".webp"


def test_extension_imagen_rechaza_formatos_invalidos():
    with pytest.raises(HTTPException) as error:
        productos._extension_imagen("application/pdf")

    assert error.value.status_code == 400
