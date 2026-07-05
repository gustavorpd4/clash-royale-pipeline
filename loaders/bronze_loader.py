import json
import os
from datetime import date

from config import BRONZE_DIR


def guardar_snapshot(data: dict, fecha: str = None) -> str:
    fecha = fecha or date.today().isoformat()
    carpeta = os.path.join(BRONZE_DIR, f"dt={fecha}")
    os.makedirs(carpeta, exist_ok=True)

    ruta = os.path.join(carpeta, "cards.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return ruta
