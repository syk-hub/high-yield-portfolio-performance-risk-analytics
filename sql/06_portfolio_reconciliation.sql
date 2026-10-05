-- Query 1: Recompute holding-level dirty market values from face value,
-- simulated clean prices, and Python-imported accrued interest. Scale
-- coupon cash from per-$100 face to USD. Values remain full precision.
SELECT
    h.internal_id,
    h.face_value_usd,
    p_begin.clean_price AS beginning_clean_price_usd_per_100_face,
    r.beginning_ai_usd_per_100_face,
    h.face_value_usd / 100
        * (p_begin.clean_price + r.beginning_ai_usd_per_100_face)
        AS beginning_dirty_market_value_usd,
    p_end.clean_price AS ending_clean_price_usd_per_100_face,
    r.ending_ai_usd_per_100_face,
    h.face_value_usd / 100
        * (p_end.clean_price + r.ending_ai_usd_per_100_face)
        AS ending_dirty_market_value_usd,
    h.face_value_usd / 100 * r.coupon_cash_usd_per_100_face
        AS coupon_cash_usd
FROM public.portfolio_holding AS h
LEFT JOIN public.simulated_price AS p_begin
    ON p_begin.internal_id = h.internal_id
   AND p_begin.valuation_date = DATE '2026-03-31'
LEFT JOIN public.simulated_price AS p_end
    ON p_end.internal_id = h.internal_id
   AND p_end.valuation_date = DATE '2026-04-30'
LEFT JOIN public.bond_return_result AS r
    ON r.internal_id = h.internal_id
ORDER BY h.internal_id;

-- Query 2: Aggregate the independently recomputed holding values.
-- Beginning cash is zero; ending NAV includes coupon cash retained
-- without interest. A NULL aggregate flags incomplete input coverage.
WITH holding_values AS (
    SELECT
        h.internal_id,
        h.face_value_usd / 100
            * (p_begin.clean_price + r.beginning_ai_usd_per_100_face)
            AS beginning_dirty_market_value_usd,
        h.face_value_usd / 100
            * (p_end.clean_price + r.ending_ai_usd_per_100_face)
            AS ending_dirty_market_value_usd,
        h.face_value_usd / 100 * r.coupon_cash_usd_per_100_face
            AS coupon_cash_usd
    FROM public.portfolio_holding AS h
    LEFT JOIN public.simulated_price AS p_begin
        ON p_begin.internal_id = h.internal_id
       AND p_begin.valuation_date = DATE '2026-03-31'
    LEFT JOIN public.simulated_price AS p_end
        ON p_end.internal_id = h.internal_id
       AND p_end.valuation_date = DATE '2026-04-30'
    LEFT JOIN public.bond_return_result AS r
        ON r.internal_id = h.internal_id
),
aggregated AS (
    SELECT
        COUNT(*) AS holding_count,
        COUNT(beginning_dirty_market_value_usd) AS beginning_value_count,
        COUNT(ending_dirty_market_value_usd) AS ending_value_count,
        COUNT(coupon_cash_usd) AS coupon_cash_count,
        SUM(beginning_dirty_market_value_usd) AS beginning_nav_usd,
        SUM(ending_dirty_market_value_usd) AS ending_dirty_bond_value_usd,
        SUM(coupon_cash_usd) AS coupon_cash_usd
    FROM holding_values
)
SELECT
    holding_count,
    CASE
        WHEN beginning_value_count = holding_count
         AND ending_value_count = holding_count
         AND coupon_cash_count = holding_count
        THEN beginning_nav_usd
    END AS beginning_nav_usd,
    CASE
        WHEN ending_value_count = holding_count
        THEN ending_dirty_bond_value_usd
    END AS ending_dirty_bond_value_usd,
    CASE
        WHEN coupon_cash_count = holding_count
        THEN coupon_cash_usd
    END AS coupon_cash_usd,
    CASE
        WHEN ending_value_count = holding_count
         AND coupon_cash_count = holding_count
        THEN ending_dirty_bond_value_usd + coupon_cash_usd
    END AS ending_nav_usd,
    CASE
        WHEN beginning_value_count = holding_count
         AND ending_value_count = holding_count
         AND coupon_cash_count = holding_count
         AND beginning_nav_usd <> 0
        THEN (
            ending_dirty_bond_value_usd + coupon_cash_usd
        ) / beginning_nav_usd - 1
    END AS portfolio_return_decimal
FROM aggregated;
