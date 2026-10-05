-- Recompute dirty bond values from simulated clean prices and imported AI.
-- Coupon cash is zero at the beginning date and is retained without interest
-- at the ending date. Benchmark face amounts use the fixed 10% beginning
-- dirty-value allocations and portfolio beginning NAV from query 08.
WITH candidate_inputs AS (
    SELECT
        b.internal_id,
        h.face_value_usd AS portfolio_face_value_usd,
        p_begin.clean_price AS beginning_clean_price,
        p_end.clean_price AS ending_clean_price,
        r.beginning_ai_usd_per_100_face,
        r.ending_ai_usd_per_100_face,
        r.coupon_cash_usd_per_100_face,
        risk_begin.effective_duration_years AS beginning_duration_years,
        risk_begin.oas_bps AS beginning_oas_bps,
        risk_end.effective_duration_years AS ending_duration_years,
        risk_end.oas_bps AS ending_oas_bps,
        (
            h.face_value_usd IS NOT NULL
            AND h.face_value_usd > 0
            AND h.face_value_usd NOT IN
                ('NaN'::NUMERIC, 'Infinity'::NUMERIC, '-Infinity'::NUMERIC)
            AND p_begin.clean_price IS NOT NULL
            AND p_begin.clean_price > 0
            AND p_begin.clean_price NOT IN
                ('NaN'::NUMERIC, 'Infinity'::NUMERIC, '-Infinity'::NUMERIC)
            AND r.beginning_ai_usd_per_100_face IS NOT NULL
            AND r.beginning_ai_usd_per_100_face >= 0
            AND r.beginning_ai_usd_per_100_face NOT IN
                ('NaN'::NUMERIC, 'Infinity'::NUMERIC, '-Infinity'::NUMERIC)
        ) AS beginning_market_inputs_valid,
        (
            p_end.clean_price IS NOT NULL
            AND p_end.clean_price > 0
            AND p_end.clean_price NOT IN
                ('NaN'::NUMERIC, 'Infinity'::NUMERIC, '-Infinity'::NUMERIC)
            AND r.ending_ai_usd_per_100_face IS NOT NULL
            AND r.ending_ai_usd_per_100_face >= 0
            AND r.ending_ai_usd_per_100_face NOT IN
                ('NaN'::NUMERIC, 'Infinity'::NUMERIC, '-Infinity'::NUMERIC)
        ) AS ending_market_inputs_valid,
        (
            r.coupon_cash_usd_per_100_face IS NOT NULL
            AND r.coupon_cash_usd_per_100_face >= 0
            AND r.coupon_cash_usd_per_100_face NOT IN
                ('NaN'::NUMERIC, 'Infinity'::NUMERIC, '-Infinity'::NUMERIC)
        ) AS coupon_input_valid,
        (
            risk_begin.effective_duration_years IS NOT NULL
            AND risk_begin.effective_duration_years > 0
            AND risk_begin.effective_duration_years NOT IN
                ('NaN'::NUMERIC, 'Infinity'::NUMERIC, '-Infinity'::NUMERIC)
            AND risk_begin.oas_bps IS NOT NULL
            AND risk_begin.oas_bps >= 0
            AND risk_begin.oas_bps NOT IN
                ('NaN'::NUMERIC, 'Infinity'::NUMERIC, '-Infinity'::NUMERIC)
        ) AS beginning_risk_inputs_valid,
        (
            risk_end.effective_duration_years IS NOT NULL
            AND risk_end.effective_duration_years > 0
            AND risk_end.effective_duration_years NOT IN
                ('NaN'::NUMERIC, 'Infinity'::NUMERIC, '-Infinity'::NUMERIC)
            AND risk_end.oas_bps IS NOT NULL
            AND risk_end.oas_bps >= 0
            AND risk_end.oas_bps NOT IN
                ('NaN'::NUMERIC, 'Infinity'::NUMERIC, '-Infinity'::NUMERIC)
        ) AS ending_risk_inputs_valid
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
    LEFT JOIN public.simulated_risk_input AS risk_begin
        ON risk_begin.internal_id = b.internal_id
       AND risk_begin.valuation_date = DATE '2026-03-31'
    LEFT JOIN public.simulated_risk_input AS risk_end
        ON risk_end.internal_id = b.internal_id
       AND risk_end.valuation_date = DATE '2026-04-30'
),
portfolio_beginning AS (
    SELECT
        COUNT(*) AS candidate_count,
        COUNT(portfolio_face_value_usd) AS portfolio_holding_count,
        COUNT(*) FILTER (
            WHERE beginning_market_inputs_valid
        ) AS complete_beginning_market_count,
        CASE
            WHEN COUNT(*) = 10
             AND COUNT(portfolio_face_value_usd) = 10
             AND COUNT(*) FILTER (
                 WHERE beginning_market_inputs_valid
             ) = 10
            THEN SUM(
                portfolio_face_value_usd / 100
                * (beginning_clean_price + beginning_ai_usd_per_100_face)
            )
        END AS portfolio_beginning_nav_usd
    FROM candidate_inputs
),
benchmark_faces AS (
    SELECT
        i.*,
        CASE
            WHEN p.portfolio_beginning_nav_usd > 0
             AND i.beginning_market_inputs_valid
            THEN p.portfolio_beginning_nav_usd * 0.10 * 100
                 / (i.beginning_clean_price
                    + i.beginning_ai_usd_per_100_face)
        END AS benchmark_face_value_usd,
        p.candidate_count,
        p.portfolio_holding_count,
        p.complete_beginning_market_count,
        p.portfolio_beginning_nav_usd
    FROM candidate_inputs AS i
    CROSS JOIN portfolio_beginning AS p
),
period_inputs AS (
    SELECT
        f.internal_id,
        f.candidate_count,
        f.portfolio_holding_count,
        f.complete_beginning_market_count,
        f.portfolio_beginning_nav_usd,
        d.valuation_date,
        d.clean_price,
        d.accrued_interest,
        d.effective_duration_years,
        d.oas_bps,
        f.coupon_cash_usd_per_100_face,
        f.coupon_input_valid,
        d.market_inputs_valid,
        d.risk_inputs_valid,
        s.portfolio_type,
        s.face_value_usd,
        (
            d.market_inputs_valid
            AND f.coupon_input_valid
            AND d.risk_inputs_valid
            AND s.face_value_usd IS NOT NULL
            AND s.face_value_usd > 0
            AND s.face_value_usd NOT IN
                ('NaN'::NUMERIC, 'Infinity'::NUMERIC, '-Infinity'::NUMERIC)
        ) AS inputs_complete
    FROM benchmark_faces AS f
    CROSS JOIN LATERAL (
        VALUES
            (
                DATE '2026-03-31',
                f.beginning_clean_price,
                f.beginning_ai_usd_per_100_face,
                f.beginning_duration_years,
                f.beginning_oas_bps,
                f.beginning_market_inputs_valid,
                f.beginning_risk_inputs_valid
            ),
            (
                DATE '2026-04-30',
                f.ending_clean_price,
                f.ending_ai_usd_per_100_face,
                f.ending_duration_years,
                f.ending_oas_bps,
                f.ending_market_inputs_valid,
                f.ending_risk_inputs_valid
            )
    ) AS d(
        valuation_date,
        clean_price,
        accrued_interest,
        effective_duration_years,
        oas_bps,
        market_inputs_valid,
        risk_inputs_valid
    )
    CROSS JOIN LATERAL (
        VALUES
            ('portfolio'::TEXT, f.portfolio_face_value_usd),
            ('benchmark'::TEXT, f.benchmark_face_value_usd)
    ) AS s(portfolio_type, face_value_usd)
),
bond_values AS (
    SELECT
        *,
        face_value_usd / 100 * (clean_price + accrued_interest)
            AS dirty_bond_market_value_usd,
        CASE
            WHEN valuation_date = DATE '2026-04-30'
            THEN face_value_usd / 100 * coupon_cash_usd_per_100_face
            ELSE 0::NUMERIC
        END AS retained_coupon_cash_usd
    FROM period_inputs
),
portfolio_risk AS (
    SELECT
        portfolio_type,
        valuation_date,
        COUNT(*) AS candidate_count,
        MIN(candidate_count) AS master_candidate_count,
        MIN(portfolio_holding_count) AS portfolio_holding_count,
        MIN(complete_beginning_market_count)
            AS complete_beginning_market_count,
        MIN(portfolio_beginning_nav_usd) AS portfolio_beginning_nav_usd,
        COUNT(*) FILTER (WHERE inputs_complete) AS complete_input_count,
        COUNT(dirty_bond_market_value_usd) AS bond_value_count,
        SUM(dirty_bond_market_value_usd) AS dirty_bond_market_value_usd,
        SUM(retained_coupon_cash_usd) AS retained_coupon_cash_usd,
        SUM(dirty_bond_market_value_usd)
            + SUM(retained_coupon_cash_usd) AS nav_usd,
        CASE
            WHEN COUNT(*) = 10
             AND COUNT(*) FILTER (WHERE inputs_complete) = 10
            THEN SUM(
                dirty_bond_market_value_usd * effective_duration_years
            ) / NULLIF(
                SUM(dirty_bond_market_value_usd)
                    + SUM(retained_coupon_cash_usd),
                0
            )
        END AS duration_years,
        CASE
            WHEN COUNT(*) = 10
             AND COUNT(*) FILTER (WHERE inputs_complete) = 10
            THEN SUM(dirty_bond_market_value_usd * oas_bps)
                 / NULLIF(SUM(dirty_bond_market_value_usd), 0)
        END AS average_oas_bps,
        CASE
            WHEN COUNT(*) = 10
             AND COUNT(*) FILTER (WHERE inputs_complete) = 10
            THEN SUM(retained_coupon_cash_usd)
                 / NULLIF(
                     SUM(dirty_bond_market_value_usd)
                         + SUM(retained_coupon_cash_usd),
                     0
                 )
        END AS cash_weight,
        CASE
            WHEN COUNT(*) = 10
             AND COUNT(*) FILTER (WHERE inputs_complete) = 10
            THEN SUM(dirty_bond_market_value_usd)
                 / NULLIF(
                     SUM(dirty_bond_market_value_usd)
                         + SUM(retained_coupon_cash_usd),
                     0
                 )
        END AS bond_nav_weight
    FROM bond_values
    GROUP BY portfolio_type, valuation_date
),
checks AS (
    SELECT
        *,
        CASE
            WHEN master_candidate_count = 10
             AND portfolio_holding_count = 10
             AND candidate_count = 10
             AND complete_input_count = 10
             AND bond_value_count = 10
             AND nav_usd > 0
            THEN 'PASS'
            ELSE 'FAIL'
        END AS coverage_status,
        CASE
            WHEN master_candidate_count = 10
             AND portfolio_holding_count = 10
             AND candidate_count = 10
             AND complete_input_count = 10
             AND ABS(bond_nav_weight + cash_weight - 1) <= 0.00000001
            THEN 'PASS'
            ELSE 'FAIL'
        END AS weights_status,
        CASE
            WHEN portfolio_type = 'benchmark'
             AND valuation_date = DATE '2026-03-31'
             AND master_candidate_count = 10
             AND complete_input_count = 10
             AND duration_years IS NOT NULL
             AND ABS(duration_years - 3.07) <= 0.000001
            THEN 'PASS'
            WHEN portfolio_type = 'benchmark'
             AND valuation_date = DATE '2026-03-31'
            THEN 'FAIL'
            ELSE 'N/A'
        END AS beginning_benchmark_duration_status,
        CASE
            WHEN portfolio_type = 'benchmark'
             AND valuation_date = DATE '2026-03-31'
             AND master_candidate_count = 10
             AND complete_input_count = 10
             AND average_oas_bps IS NOT NULL
             AND ABS(average_oas_bps - 340) <= 0.000001
            THEN 'PASS'
            WHEN portfolio_type = 'benchmark'
             AND valuation_date = DATE '2026-03-31'
            THEN 'FAIL'
            ELSE 'N/A'
        END AS beginning_benchmark_oas_status
    FROM portfolio_risk
)
SELECT
    portfolio_type,
    valuation_date,
    master_candidate_count,
    portfolio_holding_count,
    candidate_count AS bond_count,
    complete_input_count,
    CASE
        WHEN coverage_status = 'PASS'
        THEN ROUND(dirty_bond_market_value_usd, 2)
    END AS dirty_bond_market_value_usd,
    CASE
        WHEN coverage_status = 'PASS'
        THEN ROUND(retained_coupon_cash_usd, 2)
    END AS retained_coupon_cash_usd,
    CASE
        WHEN coverage_status = 'PASS' THEN ROUND(nav_usd, 2)
    END AS nav_usd,
    ROUND(duration_years, 6) AS duration_years,
    ROUND(average_oas_bps, 6) AS average_oas_bps,
    ROUND(bond_nav_weight, 8) AS bond_nav_weight,
    ROUND(cash_weight, 8) AS cash_weight,
    ROUND(bond_nav_weight + cash_weight, 8) AS total_nav_weight,
    coverage_status,
    weights_status,
    beginning_benchmark_duration_status,
    beginning_benchmark_oas_status,
    CASE
        WHEN coverage_status = 'PASS'
         AND weights_status = 'PASS'
         AND beginning_benchmark_duration_status IN ('PASS', 'N/A')
         AND beginning_benchmark_oas_status IN ('PASS', 'N/A')
        THEN 'PASS'
        ELSE 'FAIL'
    END AS overall_status
FROM checks
ORDER BY
    CASE portfolio_type WHEN 'portfolio' THEN 1 ELSE 2 END,
    valuation_date;
