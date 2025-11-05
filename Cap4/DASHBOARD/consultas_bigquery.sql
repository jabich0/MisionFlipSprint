-- Consultas KPI para BigQuery (ajusta `project.dataset`)
-- 1) % SLA
WITH envios AS (
  SELECT DISTINCT id_envio FROM `project.greendelivery.telemetria`
),
criticas AS (
  SELECT id_envio, COUNT(1) AS n_crit
  FROM `project.greendelivery.alertas_generadas`
  WHERE critica = TRUE
  GROUP BY id_envio
),
envios_join AS (
  SELECT e.id_envio, IFNULL(c.n_crit,0) AS n_crit
  FROM envios e
  LEFT JOIN criticas c USING (id_envio)
)
SELECT ROUND(100 * SUM(CASE WHEN n_crit=0 THEN 1 ELSE 0 END) / GREATEST(COUNT(1),1), 2) AS kpi_pct_sla
FROM envios_join;

-- 2) MTTD
WITH first_anom AS (
  SELECT id_envio, MIN(ts) AS ts_anom
  FROM `project.greendelivery.telemetria`
  WHERE temperatura > 8.0 OR acelerometro_ejeZ > 2.5
  GROUP BY id_envio
),
first_alert AS (
  SELECT id_envio, MIN(ts_alerta) AS ts_alerta
  FROM `project.greendelivery.alertas_generadas`
  GROUP BY id_envio
)
SELECT ROUND(AVG(TIMESTAMP_DIFF(ts_alerta, ts_anom, SECOND)), 2) AS kpi_mttd_seconds
FROM first_anom a
JOIN first_alert f USING (id_envio);

-- 3) % Falsos Positivos
SELECT ROUND(100 * SUM(CASE WHEN af.false_positive THEN 1 ELSE 0 END) / GREATEST(COUNT(1),1), 2) AS kpi_pct_false_positives
FROM `project.greendelivery.alertas_generadas` ag
LEFT JOIN `project.greendelivery.alertas_feedback` af
USING (id_envio, ts_alerta);
