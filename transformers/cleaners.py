import pandas as pd
import json
from config import BRONZE_DIR

def cargar_snapshot(fecha:str):
    try:
        path = f"{BRONZE_DIR}/dt={fecha}/cards.json"
        data = json.load(open(path))["items"]
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error al cargar el snapshot: {e}")
        return None

def detectar_cambios(df_ayer, df_hoy):
    comparacion = pd.merge(df_ayer, df_hoy, on='id', suffixes=('_ayer','_hoy'), how='outer')
    columnas_a_comparar = ['maxLevel','maxEvolutionLevel','elixirCost','rarity']
    cambios = []
    for _, fila in comparacion.iterrows():
        if pd.isna(fila['name_ayer']):
            cambios.append({
                "carta_id": fila['id'],
                "nombre": fila['name_hoy'],
                "campo_cambiado": "carta_nueva",
                "valor_anterior": None,
                "valor_nuevo": "nueva",
            })
            continue

        for columna in columnas_a_comparar:
            valor_ayer = fila[f'{columna}_ayer']
            valor_hoy = fila[f'{columna}_hoy']

            ambos_nan = pd.isna(valor_ayer) and pd.isna(valor_hoy)

            if not ambos_nan and valor_ayer != valor_hoy:
                nombre = fila['name_hoy'] if pd.notna(fila['name_hoy']) else fila['name_ayer']
                cambios.append({
                    "carta_id": fila['id'],
                    "nombre": nombre,
                    "campo_cambiado": columna,
                    "valor_anterior": valor_ayer,
                    "valor_nuevo": valor_hoy,
                })

    return cambios


if __name__ == "__main__":
    df_ayer = cargar_snapshot("2026-07-03")
    df_hoy = cargar_snapshot("2026-07-04")

    cambios = detectar_cambios(df_ayer, df_hoy)
    for c in cambios:
        print(c)
    print(f"Total cambios: {len(cambios)}")
