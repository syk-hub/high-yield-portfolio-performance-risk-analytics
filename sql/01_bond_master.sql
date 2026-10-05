CREATE TABLE bond_master (
    -- Identity and project classification.
    internal_id TEXT PRIMARY KEY,
    legal_issuer TEXT NOT NULL,
    sector TEXT NOT NULL,
    currency TEXT NOT NULL,

    -- Contractual coupon, dates, schedule, and day-count description.
    coupon_rate_decimal NUMERIC NOT NULL
        CHECK (coupon_rate_decimal BETWEEN 0 AND 1),
    maturity_date DATE NOT NULL,
    issuance_date DATE,
    coupon_month_day_1 TEXT NOT NULL
        CHECK (
            coupon_month_day_1 IS NULL
            OR coupon_month_day_1 ~ '^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'
        ),
    coupon_month_day_2 TEXT NOT NULL
        CHECK (
            coupon_month_day_2 IS NULL
            OR coupon_month_day_2 ~ '^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'
        ),
    first_coupon_date DATE NOT NULL,
    day_count_basis TEXT NOT NULL,

    -- Identifiers are text so leading characters and exact formats are retained.
    cusip TEXT,
    isin TEXT,

    -- Preserve rating text, scope, date, and source exactly as supplied.
    rating TEXT,
    rating_scope TEXT,
    rating_as_of DATE,
    rating_source_url TEXT,

    -- Contract evidence and unresolved checks remain visible without inference.
    contractual_source_url TEXT,
    call_terms_summary TEXT,
    unresolved_checks TEXT,

    CONSTRAINT bond_master_maturity_after_issuance
        CHECK (
            issuance_date IS NULL
            OR maturity_date IS NULL
            OR maturity_date > issuance_date
        )
);
