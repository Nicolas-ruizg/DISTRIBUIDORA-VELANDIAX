import pytest
from fastapi import HTTPException

from routes import usuarios
from schemas.usuario import UsuarioUpdate


def test_actualizar_usuario_requiere_cambios():
    with pytest.raises(HTTPException) as error:
        usuarios.actualizar_usuario(
            1,
            UsuarioUpdate(),
            {"id_usuario": 2, "rol": "ADMINISTRADOR"},
        )

    assert error.value.status_code == 400


def test_admin_no_puede_desactivarse_a_si_mismo():
    with pytest.raises(HTTPException) as error:
        usuarios.desactivar_usuario(
            1,
            {"id_usuario": 1, "rol": "ADMINISTRADOR"},
        )

    assert error.value.status_code == 400
