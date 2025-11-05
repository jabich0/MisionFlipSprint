-- Consultas KPI para PostgreSQL
-- Tablas:
-- telemetria(id_envio TEXT, ts TIMESTAMP, temperatura DOUBLE PRECISION, acelerometro_ejeZ DOUBLE PRECISION)
-- alertas_generadas(id_envio TEXT, ts_alerta TIMESTAMP, tipo TEXT, critica BOOLEAN)
-- alertas_feedback(id_envio TEXT, ts_alerta TIMESTAMP, false_positive BOOLEAN)

-- 1) % SLA
WITH envios AS (
  SELECT DISTINCT id_envio FROM telemetria
),
criticas AS (
  SELECT id_envio, COUNT(*) AS n_crit
  FROM alertas_generadas
  WHERE critica IS TRUE
  GROUP BY id_envio
),
envios_join AS (
  SELECT e.id_envio, COALESCE(c.n_crit,0) AS n_crit
  FROM envios e
  LEFT JOIN criticas c USING (id_envio)
)
SELECT
  ROUND(100.0 * SUM(CASE WHEN n_crit=0 THEN 1 ELSE 0 END)::numeric / GREATEST(COUNT(*),1), 2) AS kpi_pct_sla
FROM envios_join;

-- 2) MTTD (segundos)
WITH first_anom AS (
  SELECT id_envio, MIN(ts) AS ts_anom
  FROM telemetria
  WHERE temperatura > 8.0 OR acelerometro_ejeZ > 2.5
  GROUP BY id_envio
),
first_alert AS (
  SELECT id_envio, MIN(ts_alerta) AS ts_alerta
  FROM alertas_generadas
  GROUP BY id_envio
),
j AS (
  SELECT a.id_envio, a.ts_anom, f.ts_alerta
  FROM first_anom a
  JOIN first_alert f USING (id_envio)
)
SELECT ROUND(AVG(EXTRACT(EPOCH FROM (ts_alerta - ts_anom)))::numeric, 2) AS kpi_mttd_seconds
FROM j;

-- 3) % Falsos Positivos
SELECT
  ROUND(100.0 * SUM(CASE WHEN af.false_positive THEN 1 ELSE 0 END)::numeric / GREATEST(COUNT(*),1), 2) AS kpi_pct_false_positives
FROM alertas_generadas ag
LEFT JOIN alertas_feedback af
  ON ag.id_envio = af.id_envio AND ag.ts_alerta = af.ts_alerta;
