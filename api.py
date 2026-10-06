from fastapi import FastAPI, HTTPException

app = FastAPI(title="Servicio de Datos Sismológicos")

# Base de datos en memoria con datos detallados (formato sismologia.cl)
SISMOS_DB = {
    "sismo-001": {
        "id": "sismo-001",
        "fecha_hora_utc": "2026-10-05T12:00:00Z",
        "latitud": -33.036,
        "longitud": -71.629,
        "profundidad_km": 35.0,
        "magnitud": 5.2,
        "escala": "Mww",
        "referencia": "32 km al SO de Valparaíso"
    },
    "sismo-002": {
        "id": "sismo-002",
        "fecha_hora_utc": "2026-10-05T14:30:00Z",
        "latitud": -18.4746,
        "longitud": -70.29792,
        "profundidad_km": 42.1,
        "magnitud": 4.8,
        "escala": "Ml",
        "referencia": "15 km al NO de Arica"
    }
}

@app.get("/")
def home():
    return {"mensaje": "Servicio de Datos Sismológicos activo"}

@app.get("/sismos/{sismo_id}")
def obtener_sismo(sismo_id: str):
    sismo = SISMOS_DB.get(sismo_id)
    if not sismo:
        raise HTTPException(status_code=404, detail="Sismo no encontrado")
    return sismo