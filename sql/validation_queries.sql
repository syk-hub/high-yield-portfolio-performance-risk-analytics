-- Duplicate detection per snapshot
SELECT snapshot_date, bond_id, COUNT(*)
FROM holdings_snapshot
GROUP BY snapshot_date, bond_id
HAVING COUNT(*) > 1;

-- Null or missing required attributes
SELECT *
FROM bond_master
WHERE issuer IS NULL OR sector IS NULL OR rating IS NULL OR maturity_date IS NULL;

-- Reconcile dirty-market values
SELECT hs.snapshot_date, hs.bond_id,
       hs.dirty_market_value,
       (b.face_amount / 100.0) * (hs.clean_price + hs.accrued_interest) AS recomputed_dirty_value
FROM holdings_snapshot hs
JOIN bond_master b
  ON b.bond_id = hs.bond_id
WHERE ABS(hs.dirty_market_value - ((b.face_amount / 100.0) * (hs.clean_price + hs.accrued_interest))) > 0.01;

-- Check weights sum to 100% with ending cash included
SELECT
    SUM(beginning_weight) AS total_beginning_weight,
    SUM(ending_weight) AS total_ending_weight
FROM benchmark_weights;

-- Flag large clean-price movements for review
SELECT bond_id, snapshot_date, clean_price
FROM holdings_snapshot
WHERE ABS(clean_price - LAG(clean_price) OVER (PARTITION BY bond_id ORDER BY snapshot_date)) > 5.0;
