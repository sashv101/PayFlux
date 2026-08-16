PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS merchants (
    merchant_id TEXT PRIMARY KEY,
    business_name TEXT NOT NULL,
    business_type TEXT NOT NULL,
    city TEXT NOT NULL,
    kyc_status TEXT NOT NULL
        CHECK (kyc_status IN ('verified', 'pending', 'on_hold')),
    settlement_cycle_days INTEGER NOT NULL
        CHECK (settlement_cycle_days > 0),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id TEXT PRIMARY KEY,
    merchant_id TEXT NOT NULL,
    amount_paise INTEGER NOT NULL
        CHECK (amount_paise > 0),
    payment_method TEXT NOT NULL
        CHECK (payment_method IN ('upi', 'card', 'netbanking')),
    status TEXT NOT NULL
        CHECK (status IN ('captured', 'failed', 'pending')),
    failure_code TEXT,
    created_at TEXT NOT NULL,

    FOREIGN KEY (merchant_id)
        REFERENCES merchants (merchant_id)
);

CREATE TABLE IF NOT EXISTS settlements (
    settlement_id TEXT PRIMARY KEY,
    merchant_id TEXT NOT NULL,
    amount_paise INTEGER NOT NULL
        CHECK (amount_paise > 0),
    status TEXT NOT NULL
        CHECK (status IN ('scheduled', 'processed', 'delayed', 'on_hold')),
    scheduled_at TEXT NOT NULL,
    settled_at TEXT,
    hold_reason TEXT,

    FOREIGN KEY (merchant_id)
        REFERENCES merchants (merchant_id)
);

CREATE TABLE IF NOT EXISTS tickets (
    ticket_id TEXT PRIMARY KEY,
    merchant_id TEXT NOT NULL,
    payment_id TEXT,
    settlement_id TEXT,
    subject TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL
        CHECK (
            category IN (
                'payment_failed',
                'settlement_delayed',
                'kyc_review',
                'api_integration'
            )
        ),
    priority TEXT NOT NULL
        CHECK (priority IN ('low', 'medium', 'high')),
    status TEXT NOT NULL
        CHECK (status IN ('open', 'investigating', 'resolved')),
    expected_resolution TEXT NOT NULL,
    created_at TEXT NOT NULL,

    FOREIGN KEY (merchant_id)
        REFERENCES merchants (merchant_id),

    FOREIGN KEY (payment_id)
        REFERENCES payments (payment_id),

    FOREIGN KEY (settlement_id)
        REFERENCES settlements (settlement_id)
);

CREATE INDEX IF NOT EXISTS idx_payments_merchant_id
    ON payments (merchant_id);

CREATE INDEX IF NOT EXISTS idx_settlements_merchant_id
    ON settlements (merchant_id);

CREATE INDEX IF NOT EXISTS idx_tickets_merchant_id
    ON tickets (merchant_id);

CREATE INDEX IF NOT EXISTS idx_tickets_category
    ON tickets (category);