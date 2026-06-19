from services.simulador_envios import siguiente_estado


def test_secuencia_estados_envio():
    assert siguiente_estado("PENDIENTE") == "PREPARANDO"
    assert siguiente_estado("PREPARANDO") == "DESPACHADO"
    assert siguiente_estado("DESPACHADO") == "EN_TRANSITO"
    assert siguiente_estado("EN_TRANSITO") == "ENTREGADO"


def test_estado_final_no_avanza():
    assert siguiente_estado("ENTREGADO") is None
    assert siguiente_estado("CANCELADO") is None
