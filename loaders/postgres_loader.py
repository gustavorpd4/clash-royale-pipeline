import json
import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

from config import DATABASE_URL_ENV_VAR

load_dotenv()


def conectar():
    url = os.getenv(DATABASE_URL_ENV_VAR)
    if not url:
        raise ValueError(f"{DATABASE_URL_ENV_VAR} no esta configurado")
    return psycopg2.connect(url)


def guardar_cartas(df: pd.DataFrame, fecha: str):
    conn = conectar()
    cur = conn.cursor()

    for _, fila in df.iterrows():
        fila_json = fila.where(pd.notna(fila), None).to_dict()

        cur.execute(
            """
            INSERT INTO cartas_snapshot
                (fecha, carta_id, nombre, rareza, elixir, max_nivel, max_evolucion, datos_completos)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (fecha, carta_id) DO NOTHING
            """,
            (
                fecha,
                int(fila["id"]),
                fila["name"],
                fila["rarity"],
                None if pd.isna(fila["elixirCost"]) else int(fila["elixirCost"]),
                None if pd.isna(fila["maxLevel"]) else int(fila["maxLevel"]),
                None if pd.isna(fila["maxEvolutionLevel"]) else int(fila["maxEvolutionLevel"]),
                json.dumps(fila_json),
            ),
        )

    conn.commit()
    cur.close()
    conn.close()


def guardar_cambios(cambios: list, fecha: str):
    if not cambios:
        return

    conn = conectar()
    cur = conn.cursor()

    for cambio in cambios:
        valor_anterior = cambio["valor_anterior"]
        valor_nuevo = cambio["valor_nuevo"]

        cur.execute(
            """
            INSERT INTO cambios_detectados
                (fecha, carta_id, nombre, campo_cambiado, valor_anterior, valor_nuevo)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                fecha,
                int(cambio["carta_id"]),
                cambio["nombre"],
                cambio["campo_cambiado"],
                None if pd.isna(valor_anterior) else str(valor_anterior),
                None if pd.isna(valor_nuevo) else str(valor_nuevo),
            ),
        )

    conn.commit()
    cur.close()
    conn.close()


def guardar_rechazadas(rechazadas: list, fecha: str):
    if not rechazadas:
        return

    conn = conectar()
    cur = conn.cursor()

    for rechazo in rechazadas:
        item = rechazo["data"]
        error = rechazo["error"]

        cur.execute(
            """
            INSERT INTO registros_rechazados (fecha, carta_id, motivo, payload_crudo)
            VALUES (%s, %s, %s, %s)
            """,
            (
                fecha,
                item.get("id"),
                str(error),
                json.dumps(item),
            ),
        )

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    from transformers.cleaners import cargar_snapshot

    df_hoy = cargar_snapshot("2026-07-04")
    guardar_cartas(df_hoy, "2026-07-04")
    print(f"{len(df_hoy)} cartas guardadas en cartas_snapshot")
