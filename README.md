# GreenDelivery FlipSprint

## Versión remota (GitHub)

# MisionFlipSprint
Javier Silos, Javier Pino, Luis Rendón


---

## Versión local (Starter)

# GreenDelivery — Flip Sprint (E2E IoT → Cloud → Decisión)

Repositorio base para el proyecto en equipo. Incluye estructura de carpetas, Docker Compose y esqueletos
de simulación IoT, API de ingesta, flujo Node‑RED, SQL, dashboards y seguridad/compliance.

> Contexto: Transporte farmacéutico en cadena de frío (2–8°C). Incidentes: temperatura, impactos, desvíos.
> Compliance: GDP (Good Distribution Practice) y referencia del **Real Decreto 782/2013** (distribución de medicamentos).

## Cómo arrancar en 5 minutos (dev)

```bash
# 1) clona este repo y entra a la carpeta
git clone <TU_URL_REPO>.git greendelivery && cd greendelivery

# 2) copia variables de ejemplo y ajústalas
cp docker/.env.example docker/.env

# 3) levanta la infraestructura base
docker compose -f docker/docker-compose.yml --env-file docker/.env up -d --build

# 4) valida salud
# - Postgres:    localhost:5432 (Adminer en http://localhost:8080)
# - Mosquitto:   mqtt://localhost:1883
# - Node-RED:    http://localhost:1880
# - Ingest API:  http://localhost:8000/docs
```

## Estructura de carpetas
```
greendelivery/
├── edge/                         # Rol 1 – Simulador IoT
├── flows/                        # Rol 3 – Node-RED/n8n (ingesta + reintentos)
├── ingest_api/                   # Rol 2 – FastAPI + validación + persistencia
├── db/                           # Esquema SQL
├── analytics/                    # Dataset etiquetado + evaluación de reglas/ML
├── dashboards/                   # Exports/consultas de BI
├── security/                     # CIA + cumplimiento
├── diagrams/                     # Arquitectura
├── doc/                          # Informe y materiales
├── video/                        # URL demo
├── docker/                       # Compose, envs y utilidades
└── .github/                      # CI, templates
```

## Roles sugeridos (3–4 personas)
- **ROL 1 (Edge)**: simulador MQTT/HTTP seguro, reconexión, documentación.
- **ROL 2 (Ingesta/DB)**: FastAPI `/ingest` con Pydantic, inserción en Postgres, throttling alerts.
- **ROL 3 (Flujos)**: Node‑RED (MQTT‑in → validate → HTTP POST), backoff exponencial, boss‑fight.
- **ROL 4 (KPIs & Compliance)**: métricas (%SLA, MTTD, %FP), dashboards, webhooks y documentación GDP.

## Roadmap por semanas (resumen)
- **Semana 1**: Simulador + Ingesta básica + Esquema + Conectividad.
- **Semana 2**: Storage + Reglas/ML (N eventos) + Alertas.
- **Semana 3**: Dashboard + Seguridad/Compliance + Demo y documentación.

> Nota: No subas secretos. Usa `docker/.env` (no versionado) y GitHub Secrets.
