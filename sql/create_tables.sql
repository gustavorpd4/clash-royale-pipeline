CREATE TABLE cartas_snapshot (
    fecha DATE NOT NULL,
    carta_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    rareza TEXT,
    elixir INTEGER,
    max_nivel INTEGER,
    max_evolucion INTEGER,
    datos_completos JSONB,
    PRIMARY KEY (fecha, carta_id)
);

CREATE TABLE cambios_detectados (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    carta_id INTEGER NOT NULL,
    nombre TEXT,
    campo_cambiado TEXT,
    valor_anterior TEXT,
    valor_nuevo TEXT,
    UNIQUE (fecha, carta_id, campo_cambiado)
);

CREATE TABLE ejecuciones_pipeline (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    estado TEXT,
    cartas_procesadas INTEGER,
    cambios_detectados INTEGER,
    duracion_segundos NUMERIC,
    error TEXT
);

CREATE TABLE registros_rechazados (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    carta_id INTEGER,
    motivo TEXT,
    payload_crudo JSONB
);
