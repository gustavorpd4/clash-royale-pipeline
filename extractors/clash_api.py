#EXTRACTOR PRINCIPAL DE API (CARTAS)

import requests
import os
from dotenv import load_dotenv

from config import API_BASE_URL, TOKEN_ENV_VAR

load_dotenv()



def get_cards():
    TOKEN = os.getenv(TOKEN_ENV_VAR)
    if not TOKEN:
        raise ValueError(f"{TOKEN_ENV_VAR} no esta configurado")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(API_BASE_URL, headers=headers)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    from validators.schemas import validar_lista
    from loaders.bronze_loader import guardar_snapshot

    data = get_cards()

    ruta = guardar_snapshot(data)
    print(f"Snapshot guardado en: {ruta}")

    validas, rechazadas = validar_lista(data["items"])
    print(f"Cartas obtenidas: {len(data['items'])}")
    print(f"Validas: {len(validas)}")
    print(f"Rechazadas: {len(rechazadas)}")


