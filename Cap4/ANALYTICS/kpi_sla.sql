-- kpi_sla.sql: Calculate SLA (percentage of shipments without critical alerts)
WITH envios AS (
    SELECT DISTINCT id_envio FROM telemetry
),
con_alerta AS (
    SELECT DISTINCT id_envio FROM alerts WHERE is_false_positive = false
)
SELECT
    100.0 * (COUNT(e.id_envio) - COUNT(a.id_envio)) / COUNT(e.id_envio) AS kpi_envios_en_sla
FROM envios e
LEFT JOIN con_alerta a ON a.id_envio = e.id_envio;
