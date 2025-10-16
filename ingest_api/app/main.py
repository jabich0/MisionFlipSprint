from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
import os
import psycopg2
from datetime import datetime, timezone
import requests

app = FastAPI(title="GreenDelivery Ingest API")

class Telemetry(BaseModel):
    parcel_id: str = Field(min_length=1, max_length=64)
    ts: datetime
    temperature_c: float | None = None
    humidity_pct: float | None = None
    g_force: float | None = None
    lat: float | None = None
    lon: float | None = None

    @field_validator("temperature_c")
    @classmethod
    def temp_range(cls, v):
        if v is None:
            return v
        if v < -50 or v > 100:
            raise ValueError("temperature_c fuera de rango físico")
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

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "greendelivery"),
        user=os.getenv("POSTGRES_USER", "gd_user"),
        password=os.getenv("POSTGRES_PASSWORD", "gd_pass"),
    )

def maybe_alert(t: Telemetry):
    reasons = []
    if t.temperature_c is not None and (t.temperature_c > 8 or t.temperature_c < 2):
        reasons.append("Temperature out of 2-8C range")
    if t.g_force is not None and t.g_force > 2.5:
        reasons.append("G-force spike > 2.5")
    return reasons

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
                payload.parcel_id, ts, payload.temperature_c, payload.humidity_pct,
                payload.g_force, payload.lat, payload.lon
            ),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DB error: {e}")

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
