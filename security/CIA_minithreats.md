# CIA + Compliance (mínimo viable)

## Confidencialidad
- Secretos en `docker/.env` (no versionado) y GitHub Secrets para CI/CD.
- TLS en tránsito (broker y API) cuando se despliegue fuera de local.
- Tokens/JWT para paneles y API (pendiente de implementar).

## Integridad
- Validación Pydantic en `/ingest` (tipos y rangos físicos).
- Checks de carga (longitud, tipo) en Node‑RED antes de POST.
- Hash/Checksum opcional en telemetría para detección de manipulación.

## Disponibilidad
- Reintentos con backoff exponencial en Node‑RED.
- Aislar servicios en contenedores y usar colas si escala (SQS/RabbitMQ).

## Compliance
- **GDP** (Good Distribution Practice) — cadena de frío farmacéutica.
- **Real Decreto 782/2013** — distribución de medicamentos de uso humano (referencia proporcionada por el equipo).
- GDPR: geolocalización y datos personales — minimización y retención limitada.
