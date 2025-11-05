#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from google.cloud import firestore
from datetime import datetime, timezone
import pandas as pd
import json

"""
Calcula 3 KPIs desde Firestore:
- % SLA (envíos sin alertas críticas)
- MTTD (Mean Time To Detect)
- % Falsos Positivos (requiere colección alertas_feedback)

Colecciones:
- telemetria: { id_envio, timestamp (ISO/epoch), temperatura, acelerometro_ejeZ }
- alertas_generadas: { id_envio, ts_alerta (ISO/epoch), tipo, critica (bool) }
- alertas_feedback (opcional): { id_envio, ts_alerta, false_positive (bool) }

export GOOGLE_APPLICATION_CREDENTIALS=/ruta/cred.json
"""

def parse_ts(ts):
    if isinstance(ts, (int, float)):
        if ts > 1e12:
            return datetime.fromtimestamp(ts/1000.0, tz=timezone.utc)
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    if isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts.replace("Z","+00:00"))
        except Exception:
            return None
    return None

def main():
    db = firestore.Client()

    tele_rows = []
    for doc in db.collection("telemetria").stream():
        d = doc.to_dict()
        tele_rows.append({
            "id_envio": d.get("id_envio"),
            "timestamp": parse_ts(d.get("timestamp")),
            "temperatura": d.get("temperatura"),
            "acelerometro_ejeZ": d.get("acelerometro_ejeZ") or d.get("acelerometro-ejeZ"),
        })
    tele = pd.DataFrame(tele_rows).dropna(subset=["id_envio", "timestamp"])

    al_rows = []
    for doc in db.collection("alertas_generadas").stream():
        d = doc.to_dict()
        al_rows.append({
            "id_envio": d.get("id_envio"),
            "ts_alerta": parse_ts(d.get("ts_alerta") or d.get("timestamp")),
            "tipo": d.get("tipo"),
            "critica": bool(d.get("critica", True)),
        })
    alertas = pd.DataFrame(al_rows).dropna(subset=["id_envio", "ts_alerta"])

    fb_rows = []
    try:
        for doc in db.collection("alertas_feedback").stream():
            d = doc.to_dict()
            fb_rows.append({
                "id_envio": d.get("id_envio"),
                "ts_alerta": parse_ts(d.get("ts_alerta")),
                "false_positive": bool(d.get("false_positive", False))
            })
    except Exception:
        pass
    feedback = pd.DataFrame(fb_rows) if fb_rows else pd.DataFrame(columns=["id_envio","ts_alerta","false_positive"])

    envios = tele["id_envio"].dropna().unique().tolist()
    if not alertas.empty:
        criticas_por_envio = alertas[alertas["critica"]==True].groupby("id_envio").size().rename("n_crit").reset_index()
    else:
        criticas_por_envio = pd.DataFrame(columns=["id_envio","n_crit"])

    criticas_por_envio = criticas_por_envio.set_index("id_envio").reindex(envios).fillna(0).reset_index()
    envios_sin_critica = (criticas_por_envio["n_crit"]==0).sum()
    pct_sla = (envios_sin_critica / max(len(envios),1))*100.0

    UMB_TEMP = 8.0
    UMB_G = 2.5
    mttd_secs = None
    if not alertas.empty:
        tele_sorted = tele.sort_values(["id_envio","timestamp"]).copy()
        tele_sorted["anom"] = ((tele_sorted["temperatura"]>UMB_TEMP) | (tele_sorted["acelerometro_ejeZ"]>UMB_G))
        first_anom = tele_sorted[tele_sorted["anom"]==True].groupby("id_envio")["timestamp"].min().rename("ts_anom").reset_index()
        first_alert = alertas.groupby("id_envio")["ts_alerta"].min().rename("ts_alerta").reset_index()
        join = pd.merge(first_anom, first_alert, on="id_envio", how="inner")
        if not join.empty:
            diffs = (join["ts_alerta"] - join["ts_anom"]).dt.total_seconds()
            mttd_secs = max(diffs.mean(), 0.0)

    pct_fp = None
    if not alertas.empty and not feedback.empty:
        joined = pd.merge(alertas, feedback, on=["id_envio","ts_alerta"], how="left")
        total_alertas = len(joined)
        falsos = joined["false_positive"].fillna(False).sum()
        pct_fp = (falsos / total_alertas)*100.0 if total_alertas>0 else 0.0

    resumen = {
        "kpi_pct_sla": round(pct_sla,2),
        "kpi_mttd_seconds": None if mttd_secs is None else round(mttd_secs,2),
        "kpi_pct_false_positives": None if pct_fp is None else round(pct_fp,2),
        "n_envios": len(envios),
        "n_alertas": 0 if alertas.empty else int(len(alertas)),
    }
    print(json.dumps(resumen, indent=2, ensure_ascii=False))

    pd.DataFrame([resumen]).to_csv("kpis_resumen.csv", index=False)
    print("KPIs exportados a kpis_resumen.csv")

if __name__ == "__main__":
    main()
