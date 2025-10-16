# Flujos Node‑RED
Importa `node-red.json` en http://localhost:1880.

Pipeline sugerido: **MQTT in → Validate → HTTP POST** con **reintentos/backoff** (añade nodos `delay` + `catch`).

- Topic: `greendelivery/trackers/telemetry`
- API: `http://ingest_api:8000/ingest`
