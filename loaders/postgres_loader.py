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


if __name__ == "__main__":
    from transformers.cleaners import cargar_snapshot

    df_hoy = cargar_snapshot("2026-07-04")
    guardar_cartas(df_hoy, "2026-07-04")
    print(f"{len(df_hoy)} cartas guardadas en cartas_snapshot")
