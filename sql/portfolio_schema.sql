CREATE TABLE IF NOT EXISTS bond_master (
    bond_id VARCHAR(50) PRIMARY KEY,
    issuer VARCHAR(200),
    sector VARCHAR(100),
    rating VARCHAR(20),
    maturity_date DATE,
    coupon_rate DECIMAL(8,4),
    coupon_frequency INT,
    day_count_basis VARCHAR(20),
    face_amount NUMERIC(18,2),
    duration_years NUMERIC(8,4),
    oas_bp NUMERIC(10,2),
    provenance VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS holdings_snapshot (
    snapshot_date DATE,
    bond_id VARCHAR(50),
    clean_price NUMERIC(12,4),
    accrued_interest NUMERIC(12,4),
    dirty_market_value NUMERIC(18,2),
    source_provenance VARCHAR(50),
    PRIMARY KEY (snapshot_date, bond_id)
);

CREATE TABLE IF NOT EXISTS benchmark_weights (
    bond_id VARCHAR(50),
    beginning_weight NUMERIC(8,6),
    ending_weight NUMERIC(8,6),
    PRIMARY KEY (bond_id)
);

CREATE TABLE IF NOT EXISTS data_quality_exception (
    exception_id SERIAL PRIMARY KEY,
    exception_date DATE,
    bond_id VARCHAR(50),
    exception_type VARCHAR(100),
    exception_detail TEXT,
    resolution VARCHAR(200),
    resolved BOOLEAN DEFAULT FALSE
);

CREATE VIEW reconciled_portfolio AS
SELECT
    b.bond_id,
    b.issuer,
    b.sector,
    b.rating,
    hs_begin.clean_price AS begin_clean_price,
    hs_end.clean_price AS end_clean_price,
    hs_begin.accrued_interest AS begin_accrued_interest,
    hs_end.accrued_interest AS end_accrued_interest,
    hs_begin.dirty_market_value AS begin_dirty_value,
    hs_end.dirty_market_value AS end_dirty_value,
    (hs_end.dirty_market_value - hs_begin.dirty_market_value) AS dirty_value_change,
    (hs_end.dirty_market_value - hs_begin.dirty_market_value) / NULLIF(hs_begin.dirty_market_value, 0) AS total_return_proxy
FROM bond_master b
LEFT JOIN holdings_snapshot hs_begin
    ON hs_begin.bond_id = b.bond_id AND hs_begin.snapshot_date = '2026-03-31'
LEFT JOIN holdings_snapshot hs_end
    ON hs_end.bond_id = b.bond_id AND hs_end.snapshot_date = '2026-04-30';
