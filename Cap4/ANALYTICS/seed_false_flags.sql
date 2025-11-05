-- seed_false_flags.sql: Mark alerts as false positives
ALTER TABLE IF EXISTS alerts
  ADD COLUMN IF NOT EXISTS is_false_positive boolean DEFAULT false;
