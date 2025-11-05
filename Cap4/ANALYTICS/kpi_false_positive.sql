-- kpi_false_positive.sql: Calculate False Positive Rate
SELECT
    CASE WHEN COUNT(*) = 0 THEN 0
         ELSE 100.0 * SUM(CASE WHEN is_false_positive THEN 1 ELSE 0 END) / COUNT(*)
    END AS kpi_false_positive_pct
FROM alerts;
