from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
import os
import psycopg2
from datetime import datetime, timezone
import requests

app = FastAPI(title="GreenDelivery Ingest API")

# -------------------------------------------------------------
# MODELO DE ENTRADA CON VALIDACIONES
# -------------------------------------------------------------
class Telemetry(BaseModel):
    parcel_id: str = Field(min_length=1, max_length=64, description="Identificador único del paquete")
    ts: datetime = Field(description="Fecha y hora UTC de la medición")
    temperature_c: float | None = Field(default=None, description="Temperatura en °C")
    humidity_pct: float | None = Field(default=None, description="Humedad relativa en %")
    g_force: float | None = Field(default=None, description="Fuerza G registrada")
    lat: float | None = Field(default=None, description="Latitud GPS")
    lon: float | None = Field(default=None, description="Longitud GPS")

    @field_validator("temperature_c")
    @classmethod
    def temp_range(cls, v):
        if v is None:
            return v
        if v < -50 or v > 100:
            raise ValueError("temperature_c fuera de rango físico [-50,100]")
        return v

    @field_validator("humidity_pct")
    @classmethod
    def hum_range(cls, v):
        if v is None:
            return v
        if v < 0 or v > 100:
            raise ValueError("humidity_pct fuera de rango [0,100]")
        return v

    @field_validator("g_force")
    @classmethod
    def g_range(cls, v):
        if v is None:
            return v
        if v < 0 or v > 20:
            raise ValueError("g_force fuera de rango [0,20]")
        return v

    @field_validator("lat")
    @classmethod
    def lat_range(cls, v):
        if v is None:
            return v
        if v < -90 or v > 90:
            raise ValueError("lat fuera de rango [-90,90]")
        return v

    @field_validator("lon")
    @classmethod
    def lon_range(cls, v):
        if v is None:
            return v
        if v < -180 or v > 180:
            raise ValueError("lon fuera de rango [-180,180]")
        return v

    @field_validator("ts")
    @classmethod
    def valid_timestamp(cls, v: datetime):
        now = datetime.now(timezone.utc)
        if v > now.replace(minute=now.minute + 5):
            raise ValueError("timestamp no puede ser una fecha futura")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "parcel_id": "PKT-123",
                "ts": "2025-11-06T12:30:00Z",
                "temperature_c": 5.5,
                "humidity_pct": 55.2,
                "g_force": 0.98,
                "lat": 40.4168,
                "lon": -3.7038
            }
        }


# -------------------------------------------------------------
# CONEXIÓN A BASE DE DATOS
# -------------------------------------------------------------
def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "greendelivery"),
        user=os.getenv("POSTGRES_USER", "gd_user"),
        password=os.getenv("POSTGRES_PASSWORD", "gd_pass"),
    )


# -------------------------------------------------------------
# ALERTAS
# -------------------------------------------------------------
def maybe_alert(t: Telemetry):
    reasons = []
    if t.temperature_c is not None and (t.temperature_c > 8 or t.temperature_c < 2):
        reasons.append("Temperature out of 2–8 °C range")
    if t.g_force is not None and t.g_force > 2.5:
        reasons.append("G-force spike > 2.5 g")
    return reasons


# -------------------------------------------------------------
# ENDPOINT PRINCIPAL
# -------------------------------------------------------------
@app.post("/ingest")
def ingest(payload: Telemetry):
    ts = payload.ts.astimezone(timezone.utc)

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO telemetry(parcel_id, ts, temperature_c, humidity_pct, g_force, lat, lon)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                payload.parcel_id, ts, payload.temperature_c,
                payload.humidity_pct, payload.g_force, payload.lat, payload.lon
            ),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DB error: {e}")

    # Generar alertas si corresponde
    reasons = maybe_alert(payload)
    if reasons:
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO alerts(parcel_id, ts, severity, kind, reason, metadata)
                VALUES (%s,%s,%s,%s,%s,%s)
                """,
                (
                    payload.parcel_id, ts, "WARNING", "rule",
                    "; ".join(reasons), "{}"
                ),
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception:
            pass

        WEBHOOK = os.getenv("WEBHOOK_URL", "")
        if WEBHOOK.startswith("http"):
            try:
                requests.post(WEBHOOK, json={
                    "text": f"[GreenDelivery] Alerta {payload.parcel_id} @ {ts.isoformat()} — {', '.join(reasons)}"
                }, timeout=3)
            except Exception:
                pass

    return {"ok": True, "alert_reasons": reasons}
