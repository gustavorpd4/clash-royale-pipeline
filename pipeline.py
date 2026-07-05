from datetime import date, timedelta

from extractors.clash_api import get_cards
from loaders.bronze_loader import guardar_snapshot
from loaders.postgres_loader import guardar_cartas, guardar_cambios, guardar_rechazadas
from validators.schemas import validar_lista
from transformers.cleaners import cargar_snapshot, cargar_snapshot_postgres, detectar_cambios


def ejecutar():
    hoy = date.today().isoformat()
    ayer = (date.today() - timedelta(days=1)).isoformat()

    data = get_cards()
    guardar_snapshot(data, hoy)

    validas, rechazadas = validar_lista(data["items"])
    print(f"Cartas obtenidas: {len(data['items'])}")
    print(f"Validas: {len(validas)}")
    print(f"Rechazadas: {len(rechazadas)}")

    df_hoy = cargar_snapshot(hoy)
    guardar_cartas(df_hoy, hoy)
    guardar_rechazadas(rechazadas, hoy)

    df_ayer = cargar_snapshot_postgres(ayer)
    if df_ayer.empty:
        print(f"No hay snapshot de {ayer} en Postgres, se omite deteccion de cambios")
        return

    cambios = detectar_cambios(df_ayer, df_hoy)
    guardar_cambios(cambios, hoy)
    print(f"Cambios detectados: {len(cambios)}")


if __name__ == "__main__":
    ejecutar()
