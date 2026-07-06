import json

from validators.schemas import validar_lista


def test_valida_cartas_reales():
    data = json.load(open("tests/mock_card.json"))["items"]

    validas, rechazadas = validar_lista(data)

    assert len(validas) == 6
    assert len(rechazadas) == 0


def test_rechaza_carta_invalida():
    data = [{"name": "CartaRota", "id": "no-es-numero", "rarity": "common"}]

    validas, rechazadas = validar_lista(data)

    assert len(validas) == 0
    assert len(rechazadas) == 1
