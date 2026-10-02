CREATE TABLE IF NOT EXISTS scores (
    transaction_id TEXT PRIMARY KEY,
    score DOUBLE PRECISION NOT NULL,
    fraud_flag INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);