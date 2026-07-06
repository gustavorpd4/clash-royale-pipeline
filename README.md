# Clash Royale Cards Pipeline

Pipeline de datos que extrae diariamente el catálogo completo de cartas de Clash Royale desde la API oficial de Supercell, lo valida, lo almacena históricamente y detecta automáticamente cambios de balance (nuevas cartas, cartas eliminadas, cambios de elixir/rareza/nivel máximo) comparando el snapshot de hoy contra el de ayer.

## Arquitectura

```
API Supercell ──▶ Extractor ──▶ Validador (Pydantic) ──▶ Bronze (JSON, dt=YYYY-MM-DD)
                                        │                         │
                                        ▼                         ▼
                              registros_rechazados         cartas_snapshot (Postgres)
                                                                    │
                                                                    ▼
                                                    Comparación hoy vs. ayer (Pandas)
                                                                    │
                                                                    ▼
                                                          cambios_detectados (Postgres)
```

Orquestado por `pipeline.py`, ejecutado diariamente vía GitHub Actions (cron) sobre runners self-hosted.

## Stack

- **Extracción:** `requests` + `python-dotenv` contra `GET https://api.clashroyale.com/v1/cards`
- **Validación:** `Pydantic` (modelo `Card` en [validators/schemas.py](validators/schemas.py)) — separa registros válidos de rechazados
- **Transformación:** `Pandas` — carga snapshots y detecta cambios campo a campo
- **Almacenamiento bronze:** JSON local particionado estilo Hive (`data/bronze/dt=YYYY-MM-DD/cards.json`), simulando un data lake tipo S3
- **Warehouse:** PostgreSQL en Neon vía `psycopg2-binary`
- **Orquestación:** GitHub Actions, cron diario 9am UTC (4am hora Perú) + disparo manual (`workflow_dispatch`)

### Por qué runners self-hosted

La API de Supercell exige que la IP que consulta esté en una whitelist. Las IPs de los runners de GitHub-hosted son dinámicas y no se pueden whitelistear. Por eso el workflow corre en `self-hosted`, con dos runners activos como respaldo mutuo (una laptop Windows y una VM de Oracle Cloud con IP pública reservada), ambos con su IP whitelisteada en la API key.

## Estructura del proyecto

El código está organizado en capas por responsabilidad (extracción, validación, transformación, carga), con el punto de entrada y la configuración compartida en la raíz junto a los archivos de infraestructura (`Dockerfile`, `requirements.txt`) que las herramientas esperan encontrar ahí:

```
pipeline.py                  # orquestador end-to-end (punto de entrada)
config.py                    # constantes centralizadas (URLs, nombres de env vars, rutas)
Dockerfile / .dockerignore   # empaquetado del pipeline
requirements.txt

extractors/clash_api.py      # llamada a la API de Supercell
validators/schemas.py        # modelo Pydantic Card + separación válidas/rechazadas
transformers/cleaners.py     # carga de snapshots (local o Postgres) + detección de cambios
loaders/bronze_loader.py     # persiste el snapshot crudo como JSON particionado
loaders/postgres_loader.py   # inserta cartas, cambios, rechazos y ejecuciones en Neon

sql/create_tables.sql        # DDL de las tablas del warehouse
.github/workflows/           # cron diario (self-hosted)
tests/                       # pytest: detección de cambios y validación
```

## Tablas en Postgres (Neon)

| Tabla | Propósito |
|---|---|
| `cartas_snapshot` | Snapshot desnormalizado por día, PK `(fecha, carta_id)`, incluye el JSON completo en `datos_completos` |
| `cambios_detectados` | Diffs campo a campo entre el snapshot de ayer y el de hoy |
| `registros_rechazados` | Registros que fallaron la validación Pydantic, con el payload crudo |
| `ejecuciones_pipeline` | Una fila por corrida: estado (éxito/error), cartas procesadas, cambios detectados, duración y mensaje de error si falló |

## Qué detecta `detectar_cambios`

Compara cada carta existente en ambos días contra `maxLevel`, `maxEvolutionLevel`, `elixirCost` y `rarity`, más dos casos especiales: `carta_nueva` (aparece hoy, no existía ayer) y `carta_eliminada` (existía ayer, no aparece hoy).

**Limitación conocida:** la API oficial no expone daño, HP ni velocidad de ataque, así que un balance patch que solo toque esos valores no se detecta con la fuente actual. Evaluando sumar RoyaleAPI/cr-api-data para cubrir ese caso.

## Cómo correrlo localmente

```bash
pip install -r requirements.txt
# crear .env con CLASH_API_TOKEN y DATABASE_URL
python -m pipeline
```
