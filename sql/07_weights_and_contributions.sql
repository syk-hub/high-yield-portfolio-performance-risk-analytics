-- Query 1: Recompute dirty market values and coupon cash from face,
-- simulated clean prices, and imported Python accrued interest. Then
-- show beginning weights and total-return contributions as percentages
-- and percentage points. Arithmetic remains full-precision NUMERIC.
WITH holding_values AS (
    SELECT
        h.internal_id,
        h.face_value_usd,
        h.face_value_usd / 100
            * (p_begin.clean_price + r.beginning_ai_usd_per_100_face)
            AS beginning_dirty_market_value_usd,
        h.face_value_usd / 100
            * (p_end.clean_price + r.ending_ai_usd_per_100_face)
            AS ending_dirty_market_value_usd,
        h.face_value_usd / 100 * r.coupon_cash_usd_per_100_face
            AS coupon_cash_usd,
        r.total_return_decimal,
        (
            p_begin.clean_price IS NOT NULL
            AND p_end.clean_price IS NOT NULL
            AND r.beginning_ai_usd_per_100_face IS NOT NULL
            AND r.ending_ai_usd_per_100_face IS NOT NULL
            AND r.coupon_cash_usd_per_100_face IS NOT NULL
            AND r.total_return_decimal IS NOT NULL
        ) AS inputs_complete
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
totals AS (
    SELECT
        COUNT(*) AS holding_count,
        COUNT(*) FILTER (WHERE inputs_complete) AS complete_count,
        c.candidate_count,
        c.candidate_holding_count,
        SUM(beginning_dirty_market_value_usd) AS beginning_nav_usd
    FROM holding_values
    CROSS JOIN (
        SELECT
            COUNT(*) AS candidate_count,
            COUNT(h.internal_id) AS candidate_holding_count
        FROM public.bond_master AS b
        LEFT JOIN public.portfolio_holding AS h
            ON h.internal_id = b.internal_id
    ) AS c
    GROUP BY c.candidate_count, c.candidate_holding_count
)
SELECT
    v.internal_id,
    v.face_value_usd,
    v.beginning_dirty_market_value_usd,
    v.ending_dirty_market_value_usd,
    v.coupon_cash_usd,
    CASE
        WHEN t.holding_count = 10
         AND t.candidate_count = 10
         AND t.candidate_holding_count = 10
         AND t.complete_count = 10
         AND t.beginning_nav_usd > 0
        THEN v.beginning_dirty_market_value_usd / t.beginning_nav_usd * 100
    END AS beginning_weight_percent,
    CASE
        WHEN t.holding_count = 10
         AND t.candidate_count = 10
         AND t.candidate_holding_count = 10
         AND t.complete_count = 10
        THEN v.total_return_decimal * 100
    END AS bond_total_return_percent,
    CASE
        WHEN t.holding_count = 10
         AND t.candidate_count = 10
         AND t.candidate_holding_count = 10
         AND t.complete_count = 10
         AND t.beginning_nav_usd > 0
        THEN (
            v.beginning_dirty_market_value_usd / t.beginning_nav_usd
        ) * v.total_return_decimal * 100
    END AS contribution_percentage_points
FROM holding_values AS v
CROSS JOIN totals AS t
ORDER BY v.internal_id;

-- Query 2: Independently verify ten candidate/holding rows, complete
-- price and Python-result coverage, unit-sum beginning weights, and
-- contribution reconciliation to NAV return. The final status is FAIL
-- for missing inputs, incomplete/incorrect coverage, or excess difference.
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
            AS coupon_cash_usd,
        r.total_return_decimal,
        (
            p_begin.clean_price IS NOT NULL
            AND p_end.clean_price IS NOT NULL
            AND r.beginning_ai_usd_per_100_face IS NOT NULL
            AND r.ending_ai_usd_per_100_face IS NOT NULL
            AND r.coupon_cash_usd_per_100_face IS NOT NULL
            AND r.total_return_decimal IS NOT NULL
        ) AS inputs_complete
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
coverage AS (
    SELECT
        COUNT(*) AS candidate_count,
        COUNT(h.internal_id) AS candidate_holding_count
    FROM public.bond_master AS b
    LEFT JOIN public.portfolio_holding AS h
        ON h.internal_id = b.internal_id
),
aggregated AS (
    SELECT
        COUNT(*) AS holding_count,
        COUNT(*) FILTER (WHERE inputs_complete) AS complete_input_count,
        SUM(beginning_dirty_market_value_usd) AS beginning_nav_usd,
        SUM(ending_dirty_market_value_usd) AS ending_dirty_bond_value_usd,
        SUM(coupon_cash_usd) AS total_coupon_cash_usd
    FROM holding_values
),
weighted_values AS (
    SELECT
        v.*,
        v.beginning_dirty_market_value_usd
            / NULLIF(a.beginning_nav_usd, 0) AS beginning_weight
    FROM holding_values AS v
    CROSS JOIN aggregated AS a
),
weight_and_contribution_totals AS (
    SELECT
        SUM(beginning_weight) AS beginning_weight_sum,
        SUM(beginning_weight * total_return_decimal)
            AS contribution_return_decimal
    FROM weighted_values
),
reconciliation AS (
    SELECT
        a.*,
        w.beginning_weight_sum,
        w.contribution_return_decimal,
        c.candidate_count,
        c.candidate_holding_count,
        (
            a.ending_dirty_bond_value_usd + a.total_coupon_cash_usd
        ) / NULLIF(a.beginning_nav_usd, 0) - 1 AS nav_return_decimal
    FROM aggregated AS a
        CROSS JOIN weight_and_contribution_totals AS w
        CROSS JOIN coverage AS c
)
SELECT
    candidate_count,
    candidate_holding_count,
    holding_count,
    complete_input_count,
    beginning_weight_sum,
    contribution_return_decimal,
    nav_return_decimal,
    ABS(contribution_return_decimal - nav_return_decimal)
        AS absolute_return_difference,
    CASE
        WHEN candidate_count = 10
         AND candidate_holding_count = 10
         AND holding_count = 10
         AND complete_input_count = 10
         AND beginning_nav_usd > 0
         AND ABS(beginning_weight_sum - 1) <= 0.00000001
         AND ABS(contribution_return_decimal - nav_return_decimal)
             <= 0.00000001
        THEN 'PASS'
        ELSE 'FAIL'
    END AS reconciliation_status
FROM reconciliation;
