import pandas as pd

from transformers.cleaners import detectar_cambios


def _card(id, name, max_level=14, max_evo=None, elixir=3, rarity="common"):
    return {
        "id": id,
        "name": name,
        "maxLevel": max_level,
        "maxEvolutionLevel": max_evo,
        "elixirCost": elixir,
        "rarity": rarity,
    }


def test_sin_cambios():
    df = pd.DataFrame([_card(1, "Knight")])
    assert detectar_cambios(df, df) == []


def test_carta_nueva():
    df_ayer = pd.DataFrame([_card(1, "Knight")])
    df_hoy = pd.DataFrame([_card(1, "Knight"), _card(2, "Ronin")])

    cambios = detectar_cambios(df_ayer, df_hoy)

    assert len(cambios) == 1
    assert cambios[0]["campo_cambiado"] == "carta_nueva"
    assert cambios[0]["carta_id"] == 2


def test_carta_eliminada():
    df_ayer = pd.DataFrame([_card(1, "Knight"), _card(2, "Ronin")])
    df_hoy = pd.DataFrame([_card(1, "Knight")])

    cambios = detectar_cambios(df_ayer, df_hoy)

    assert len(cambios) == 1
    assert cambios[0]["campo_cambiado"] == "carta_eliminada"
    assert cambios[0]["carta_id"] == 2


def test_cambio_elixir():
    df_ayer = pd.DataFrame([_card(1, "Knight", elixir=3)])
    df_hoy = pd.DataFrame([_card(1, "Knight", elixir=4)])

    cambios = detectar_cambios(df_ayer, df_hoy)

    assert len(cambios) == 1
    assert cambios[0]["campo_cambiado"] == "elixirCost"
    assert cambios[0]["valor_anterior"] == 3
    assert cambios[0]["valor_nuevo"] == 4


def test_cambio_rareza():
    df_ayer = pd.DataFrame([_card(1, "Knight", rarity="common")])
    df_hoy = pd.DataFrame([_card(1, "Knight", rarity="rare")])

    cambios = detectar_cambios(df_ayer, df_hoy)

    assert len(cambios) == 1
    assert cambios[0]["campo_cambiado"] == "rarity"


def test_cambio_max_level():
    df_ayer = pd.DataFrame([_card(1, "Knight", max_level=13)])
    df_hoy = pd.DataFrame([_card(1, "Knight", max_level=14)])

    cambios = detectar_cambios(df_ayer, df_hoy)

    assert len(cambios) == 1
    assert cambios[0]["campo_cambiado"] == "maxLevel"


def test_cambio_evolucion():
    df_ayer = pd.DataFrame([_card(1, "Knight", max_evo=1)])
    df_hoy = pd.DataFrame([_card(1, "Knight", max_evo=2)])

    cambios = detectar_cambios(df_ayer, df_hoy)

    assert len(cambios) == 1
    assert cambios[0]["campo_cambiado"] == "maxEvolutionLevel"
