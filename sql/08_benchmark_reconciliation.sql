-- Rebuild beginning and ending dirty prices per $100 face from simulated
-- clean prices and imported accrued interest. Allocate portfolio beginning
-- NAV equally across the ten bonds, derive fractional face amounts, and hold
-- those face amounts fixed through the period. Coupon cash earns zero interest.
WITH bond_inputs AS (
    SELECT
        b.internal_id,
        h.face_value_usd AS portfolio_face_value_usd,
        p_begin.clean_price
            + r.beginning_ai_usd_per_100_face
            AS beginning_dirty_price_usd_per_100_face,
        p_end.clean_price
            + r.ending_ai_usd_per_100_face
            AS ending_dirty_price_usd_per_100_face,
        r.coupon_cash_usd_per_100_face,
        r.total_return_decimal,
        (
            h.face_value_usd IS NOT NULL
            AND p_begin.clean_price IS NOT NULL
            AND p_end.clean_price IS NOT NULL
            AND r.beginning_ai_usd_per_100_face IS NOT NULL
            AND r.ending_ai_usd_per_100_face IS NOT NULL
            AND r.coupon_cash_usd_per_100_face IS NOT NULL
            AND r.total_return_decimal IS NOT NULL
        ) AS inputs_complete
    FROM public.bond_master AS b
    LEFT JOIN public.portfolio_holding AS h
        ON h.internal_id = b.internal_id
    LEFT JOIN public.simulated_price AS p_begin
        ON p_begin.internal_id = b.internal_id
       AND p_begin.valuation_date = DATE '2026-03-31'
    LEFT JOIN public.simulated_price AS p_end
        ON p_end.internal_id = b.internal_id
       AND p_end.valuation_date = DATE '2026-04-30'
    LEFT JOIN public.bond_return_result AS r
        ON r.internal_id = b.internal_id
),
portfolio_totals AS (
    SELECT
        COUNT(*) AS candidate_count,
        COUNT(portfolio_face_value_usd) AS portfolio_holding_count,
        COUNT(*) FILTER (WHERE inputs_complete) AS complete_input_count,
        SUM(
            portfolio_face_value_usd / 100
            * beginning_dirty_price_usd_per_100_face
        ) AS portfolio_beginning_nav_usd,
        SUM(
            portfolio_face_value_usd / 100
            * ending_dirty_price_usd_per_100_face
        ) AS portfolio_ending_dirty_bond_value_usd,
        SUM(
            portfolio_face_value_usd / 100
            * coupon_cash_usd_per_100_face
        ) AS portfolio_coupon_cash_usd
    FROM bond_inputs
),
benchmark_faces AS (
    SELECT
        i.*,
        t.portfolio_beginning_nav_usd AS benchmark_beginning_capital_usd,
        CASE
            WHEN t.portfolio_beginning_nav_usd > 0
             AND i.beginning_dirty_price_usd_per_100_face > 0
            THEN t.portfolio_beginning_nav_usd * 0.10 * 100
                 / i.beginning_dirty_price_usd_per_100_face
        END AS benchmark_face_value_usd,
        t.portfolio_beginning_nav_usd
    FROM bond_inputs AS i
    CROSS JOIN portfolio_totals AS t
),
benchmark_bonds AS (
    SELECT
        f.*,
        CASE
            WHEN benchmark_beginning_capital_usd > 0
            THEN benchmark_face_value_usd / 100
                 * beginning_dirty_price_usd_per_100_face
                 / benchmark_beginning_capital_usd
        END AS benchmark_beginning_weight,
        portfolio_face_value_usd / 100
            * beginning_dirty_price_usd_per_100_face
            / NULLIF(benchmark_beginning_capital_usd, 0)
            AS portfolio_beginning_weight,
        CASE
            WHEN inputs_complete
            THEN benchmark_face_value_usd / 100
                 * ending_dirty_price_usd_per_100_face
        END AS benchmark_ending_dirty_market_value_usd,
        CASE
            WHEN inputs_complete
            THEN benchmark_face_value_usd / 100
                 * coupon_cash_usd_per_100_face
        END AS benchmark_coupon_cash_usd
    FROM benchmark_faces AS f
),
benchmark_totals AS (
    SELECT
        MIN(benchmark_beginning_weight) AS minimum_benchmark_weight,
        MAX(benchmark_beginning_weight) AS maximum_benchmark_weight,
        SUM(benchmark_beginning_weight) AS benchmark_beginning_weight_sum,
        SUM(benchmark_ending_dirty_market_value_usd)
            AS benchmark_ending_dirty_bond_value_usd,
        SUM(benchmark_coupon_cash_usd) AS benchmark_coupon_cash_usd,
        AVG(total_return_decimal) AS average_bond_return_decimal,
        SUM(
            (portfolio_beginning_weight - 0.10) * total_return_decimal
        ) AS active_return_attribution_decimal,
        SUM(portfolio_beginning_weight - 0.10)
            AS active_weight_sum
    FROM benchmark_bonds
),
reconciliation AS (
    SELECT
        p.*,
        b.*,
        (
            p.portfolio_ending_dirty_bond_value_usd
            + p.portfolio_coupon_cash_usd
        ) / NULLIF(p.portfolio_beginning_nav_usd, 0) - 1
            AS portfolio_return_decimal,
        (
            b.benchmark_ending_dirty_bond_value_usd
            + b.benchmark_coupon_cash_usd
        ) / NULLIF(p.portfolio_beginning_nav_usd, 0) - 1
            AS benchmark_return_decimal
    FROM portfolio_totals AS p
    CROSS JOIN benchmark_totals AS b
),
checks AS (
    SELECT
        r.*,
        CASE
            WHEN candidate_count = 10
             AND portfolio_holding_count = 10
             AND complete_input_count = 10
             AND portfolio_beginning_nav_usd > 0
            THEN 'PASS'
            ELSE 'FAIL'
        END AS coverage_status,
        CASE
            WHEN candidate_count = 10
             AND complete_input_count = 10
             AND ABS(minimum_benchmark_weight - 0.10) <= 0.00000001
             AND ABS(maximum_benchmark_weight - 0.10) <= 0.00000001
             AND ABS(benchmark_beginning_weight_sum - 1)
                 <= 0.00000001
            THEN 'PASS'
            ELSE 'FAIL'
        END AS benchmark_weights_status,
        CASE
            WHEN complete_input_count = 10
             AND benchmark_return_decimal IS NOT NULL
             AND average_bond_return_decimal IS NOT NULL
             AND ABS(
                 benchmark_return_decimal - average_bond_return_decimal
             ) <= 0.00000001
            THEN 'PASS'
            ELSE 'FAIL'
        END AS benchmark_return_status,
        CASE
            WHEN complete_input_count = 10
             AND portfolio_return_decimal IS NOT NULL
             AND benchmark_return_decimal IS NOT NULL
             AND active_return_attribution_decimal IS NOT NULL
             AND ABS(
                 portfolio_return_decimal - benchmark_return_decimal
                 - active_return_attribution_decimal
             ) <= 0.00000001
            THEN 'PASS'
            ELSE 'FAIL'
        END AS active_return_status,
        CASE
            WHEN complete_input_count = 10
             AND active_weight_sum IS NOT NULL
             AND ABS(active_weight_sum) <= 0.00000001
            THEN 'PASS'
            ELSE 'FAIL'
        END AS active_weights_status
    FROM reconciliation AS r
)
SELECT
    candidate_count,
    portfolio_holding_count,
    complete_input_count,
    portfolio_beginning_nav_usd,
    portfolio_ending_dirty_bond_value_usd,
    portfolio_coupon_cash_usd,
    portfolio_return_decimal,
    portfolio_beginning_nav_usd AS benchmark_beginning_capital_usd,
    minimum_benchmark_weight,
    maximum_benchmark_weight,
    benchmark_beginning_weight_sum,
    benchmark_ending_dirty_bond_value_usd,
    benchmark_coupon_cash_usd,
    benchmark_ending_dirty_bond_value_usd
        + benchmark_coupon_cash_usd AS benchmark_ending_nav_usd,
    benchmark_return_decimal,
    average_bond_return_decimal,
    active_return_attribution_decimal,
    active_weight_sum,
    coverage_status,
    benchmark_weights_status,
    benchmark_return_status,
    active_return_status,
    active_weights_status,
    CASE
        WHEN coverage_status = 'PASS'
         AND benchmark_weights_status = 'PASS'
         AND benchmark_return_status = 'PASS'
         AND active_return_status = 'PASS'
         AND active_weights_status = 'PASS'
        THEN 'PASS'
        ELSE 'FAIL'
    END AS overall_status
FROM checks;
