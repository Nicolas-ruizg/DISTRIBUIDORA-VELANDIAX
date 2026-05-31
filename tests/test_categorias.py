import pytest
from fastapi import HTTPException

from routes import categorias
from schemas.categoria import CategoriaCreate, CategoriaUpdate


class CursorFalso:
    def __init__(self, filas=None):
        self.filas = filas or []
        self.consultas = []

    def execute(self, query, params=None):
        self.consultas.append((" ".join(query.split()), params))

    def fetchall(self):
        return self.filas

    def fetchone(self):
        return self.filas[0] if self.filas else None

    def close(self):
        pass


class ConexionFalsa:
    def __init__(self, filas=None):
        self.cursor_falso = CursorFalso(filas)
        self.confirmada = False
        self.revertida = False

    def cursor(self):
        return self.cursor_falso

    def commit(self):
        self.confirmada = True

    def rollback(self):
        self.revertida = True

    def close(self):
        pass


def test_listar_categorias(monkeypatch):
    conexion = ConexionFalsa([(2, "Calzado", True), (1, "Camisas", True)])
    monkeypatch.setattr(categorias, "get_connection", lambda: conexion)

    respuesta = categorias.listar_categorias({"rol": "ADMINISTRADOR"})

    assert respuesta == [
        {"id_categoria": 2, "nombre_categoria": "Calzado", "activa": True},
        {"id_categoria": 1, "nombre_categoria": "Camisas", "activa": True},
    ]


def test_crear_categoria(monkeypatch):
    conexion = ConexionFalsa([(6, "Accesorios", True)])
    monkeypatch.setattr(categorias, "get_connection", lambda: conexion)

    respuesta = categorias.crear_categoria(
        CategoriaCreate(nombre_categoria="Accesorios"),
        {"rol": "ADMINISTRADOR"},
    )

    assert respuesta["id_categoria"] == 6
    assert conexion.confirmada is True


def test_actualizar_categoria_requiere_cambios():
    with pytest.raises(HTTPException) as error:
        categorias.actualizar_categoria(
            1,
            CategoriaUpdate(),
            {"rol": "ADMINISTRADOR"},
        )

    assert error.value.status_code == 400

