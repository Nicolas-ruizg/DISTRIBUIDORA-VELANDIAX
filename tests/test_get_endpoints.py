from routes import categorias, pedidos, productos


class CursorFalso:
    def __init__(self, filas_por_consulta):
        self.filas_por_consulta = list(filas_por_consulta)
        self.consultas = []

    def execute(self, query, params=None):
        self.consultas.append((" ".join(query.split()), params))

    def fetchall(self):
        return self.filas_por_consulta.pop(0)

    def fetchone(self):
        filas = self.filas_por_consulta.pop(0)
        return filas[0] if filas else None

    def close(self):
        pass


class ConexionFalsa:
    def __init__(self, filas_por_consulta):
        self.cursor_falso = CursorFalso(filas_por_consulta)

    def cursor(self):
        return self.cursor_falso

    def close(self):
        pass


def test_listar_categorias_usa_tabla_nueva(monkeypatch):
    conexion = ConexionFalsa([[(1, "Ropa Deportiva", "Descripcion")]])
    monkeypatch.setattr(categorias, "get_connection", lambda: conexion)

    respuesta = categorias.listar_categorias()

    assert respuesta == [
        {
            "id_categoria": 1,
            "nombre": "Ropa Deportiva",
            "descripcion": "Descripcion",
        }
    ]
    assert "FROM categoria" in conexion.cursor_falso.consultas[0][0]


def test_listar_productos_incluye_precio_desde(monkeypatch):
    conexion = ConexionFalsa(
        [[(1, 2, "Ropa Deportiva", "Camiseta", "Dry fit", False, 2, 12)]]
    )
    monkeypatch.setattr(productos, "get_connection", lambda: conexion)

    respuesta = productos.listar_productos()

    assert respuesta[0]["nombre"] == "Camiseta"
    assert respuesta[0]["variantes"] == 2
    assert "FROM producto p" in conexion.cursor_falso.consultas[0][0]


def test_obtener_producto_devuelve_variantes(monkeypatch):
    conexion = ConexionFalsa(
        [
            [(1, 2, "Ropa Deportiva", "Camiseta", "Dry fit", False)],
            [(3, 5, 12, 8.5, 0.15, True, {"talla": "M"})],
        ]
    )
    monkeypatch.setattr(productos, "get_connection", lambda: conexion)

    respuesta = productos.obtener_producto(1)

    assert respuesta["id_producto"] == 1
    assert respuesta["variantes"][0]["atributos"] == {"talla": "M"}


def test_listar_pedidos_usa_tabla_pedido(monkeypatch):
    conexion = ConexionFalsa(
        [[(1, 1, "Carlos", "+57300", "Entregado", 47, 5, False, "2026-06-10", 2)]]
    )
    monkeypatch.setattr(pedidos, "get_connection", lambda: conexion)

    respuesta = pedidos.listar_pedidos({"rol": "ADMINISTRADOR"})

    assert respuesta[0]["cliente"] == "Carlos"
    assert "FROM pedido p" in conexion.cursor_falso.consultas[0][0]

