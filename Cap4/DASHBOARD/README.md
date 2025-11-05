# Capítulo 4 – KPIs que importan (Guía)

Este paquete incluye:
- `kpis_firestore.py` (KPIs directo desde Firestore, genera `kpis_resumen.csv`)
- `consultas_postgres.sql`
- `consultas_bigquery.sql`

## Firestore (recomendado con tu arquitectura GCP)

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/ruta/cred.json
pip install google-cloud-firestore pandas
python kpis_firestore.py
```

Crea `kpis_resumen.csv` que puedes conectar a Looker Studio / Power BI (Importar CSV) o subir a BigQuery.

### Requisito para % FP
Crea la colección `alertas_feedback` con documentos `{ id_envio, ts_alerta, false_positive }`.

## Postgres / BigQuery
Usa los SQL correspondientes si tus datos están allí.
