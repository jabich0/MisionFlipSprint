-- kpi_mttd.sql: Calculate MTTD (Mean Time To Detection)
WITH primeros_anomalos AS (
    SELECT id_envio, MIN(ts) AS ts_anomalo
    FROM telemetry
    WHERE temperatura > 8.0 OR fuerza_g > 2.5
    GROUP BY id_envio
),
primera_alerta AS (
    SELECT id_envio, MIN(ts_alerta) AS ts_alerta
    FROM alerts
    WHERE is_false_positive = false
    GROUP BY id_envio
)
SELECT AVG(EXTRACT(EPOCH FROM (pa.ts_alerta - pe.ts_anomalo))) AS mttd_seconds
FROM primeros_anomalos pe
JOIN primera_alerta pa USING (id_envio);
