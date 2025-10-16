CREATE TABLE IF NOT EXISTS telemetry (
  id BIGSERIAL PRIMARY KEY,
  parcel_id VARCHAR(64) NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  temperature_c NUMERIC(5,2),
  humidity_pct NUMERIC(5,2),
  g_force NUMERIC(6,3),
  lat NUMERIC(9,6),
  lon NUMERIC(9,6)
);
CREATE INDEX IF NOT EXISTS idx_tel_parcel_ts ON telemetry(parcel_id, ts DESC);

CREATE TABLE IF NOT EXISTS alerts (
  id BIGSERIAL PRIMARY KEY,
  parcel_id VARCHAR(64) NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  severity VARCHAR(16) NOT NULL,
  kind VARCHAR(32) NOT NULL,
  reason TEXT,
  metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_alerts_parcel_ts ON alerts(parcel_id, ts DESC);
