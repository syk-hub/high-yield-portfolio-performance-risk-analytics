# Implemented PostgreSQL Workflow

## Scope and responsibilities

The current SQL workflow covers ten candidate bonds and the valuation dates
March 31 and April 30, 2026. The scripts are in `sql/01_...sql` through
`sql/09_...sql`. Python remains responsible for coupon schedules and accrued
interest (AI); PostgreSQL stores the provided inputs and imported bond-return
results, then independently recomputes portfolio, benchmark, contribution,
and risk figures.

Scripts 06–09 were manually run in a local PostgreSQL database through
pgAdmin; the implemented reconciliation checks returned passing results.
Those checks do not establish a production deployment or automated
comparison against every Python export.

## Tables created by scripts 01–05

1. **`sql/01_bond_master.sql` — `public.bond_master`.** One row per bond,
   keyed by `internal_id`. Its 20 columns match
   `inputs/bond_candidates.csv`:
   issuer/classification, coupon and contractual dates, identifiers,
   rating text and scope, evidence URLs, call summary, and unresolved checks.
   Full dates use `DATE`, coupon rate uses `NUMERIC`, and identifiers,
   evidence, and descriptive fields use `TEXT`. Missing evidence remains
   nullable. Rating text is preserved as supplied; it is not split into
   independently verified agency records. No separate evidence table is
   currently implemented.
2. **`sql/02_simulated_price.sql` — `public.simulated_price`.** One simulated
   clean price per bond/date, keyed by (`internal_id`, `valuation_date`),
   with a foreign key to `bond_master` and positive, finite price check.
   Load from `inputs/simulated_prices.csv`.
3. **`sql/03_portfolio_holding.sql` — `public.portfolio_holding`.** One
   positive finite USD face amount per bond, keyed by `internal_id` and
   referencing `bond_master`. Load from `inputs/portfolio_holdings.csv`.
4. **`sql/04_simulated_risk_input.sql` — `public.simulated_risk_input`.**
   One simulated effective duration in years and OAS in basis points per
   bond/date, keyed by (`internal_id`, `valuation_date`). Duration must be
   positive and finite; OAS must be nonnegative and finite. Load from
   `inputs/simulated_risk_inputs.csv`.
5. **`sql/05_bond_return_result.sql` — `public.bond_return_result`.**
   Stores per-$100-face beginning/ending AI, coupon cash, dirty prices, and
   decimal price, income, and total returns, plus coupon-payment-date text
   and result status. Load from `outputs/bond_returns.csv`. The CSV has no
   period-date columns, so this single-period table is keyed by
   `internal_id`, not a multi-period key.

These CSVs are files on disk; they are imported as rows into database
tables. They are not themselves tables. Create each table before importing
its corresponding CSV, use the CSV header/column order, and load
`bond_master` before tables that reference it.

## Read-only reconciliation queries 06–09

Execute these after the five tables are populated:

- **`sql/06_portfolio_reconciliation.sql`:** shows holding-level beginning
  and ending dirty market values and coupon cash, then aggregates beginning
  NAV, ending bond value, coupon cash, ending NAV, and portfolio return.
  Dirty prices are clean prices plus imported Python AI.
- **`sql/07_weights_and_contributions.sql`:** displays beginning weights,
  imported bond total returns, and weight-based contributions. Its second
  query checks ten candidate/holding rows, complete inputs, weight sum, and
  contribution reconciliation to NAV return; missing inputs produce `FAIL`.
- **`sql/08_benchmark_reconciliation.sql`:** constructs the benchmark with
  10% beginning dirty-market-value weight in each bond and portfolio
  beginning NAV as capital. It derives fractional face amounts from
  beginning dirty prices, holds face fixed, and retains coupon cash at zero
  interest. It checks coverage, benchmark weights/return, active-return
  attribution, and active weights.
- **`sql/09_risk_reconciliation.sql`:** calculates portfolio and constructed
  benchmark risk at both dates using dirty bond values. Duration is
  market-value weighted with NAV (including cash) as denominator; average
  OAS is bond-market-value weighted; retained coupon cash contributes to
  ending NAV and cash weight. It checks ten-bond input coverage, bond plus
  cash NAV weights, and the beginning benchmark's 3.07-year duration and
  340-bps OAS.

The queries use the fixed dates and ten-bond scope. They do not generate
prices, coupon schedules, AI, holdings, or Python return outputs.

## Data evidence and genuine limitations

`inputs/bond_candidates.csv` maps directly, column for column, into the
evidence-preserving fields of `bond_master`. Keep original rating text,
rating scope, as-of date, URLs, call summary, and unresolved checks as
provided. Do not infer missing ratings, identifiers, dates, or call terms;
do not automatically convert combined agency text into verified individual
ratings. The current schema does not normalize evidence into a separate
evidence table.

Only `outputs/bond_returns.csv` has a corresponding result table in the
current DDL. There are no SQL import/comparison tables for
`outputs/portfolio_contributions.csv`, `outputs/active_contributions.csv`,
`outputs/performance_summary.csv`, or
`outputs/risk_exposure_summary.csv`. Queries 06–09 independently recompute
and reconcile relationships among the loaded input and bond-return tables,
but they do not compare every computed row with those four Python export
files. In particular, no SQL process verifies external source evidence,
actual market prices, high-yield eligibility, or simulation assumptions.

The implemented decimal-return and weight checks use `0.00000001`;
duration and OAS checks use `0.000001` years and bps, respectively.
The design target of $0.01 for dollar comparisons is not currently applied
as a comparison against imported summary exports. Python CSVs serialize
numeric values as decimal text with precision sufficient for the stated
decimal, duration, and OAS tolerances; import them as PostgreSQL `NUMERIC`
without rounding or conversion through binary floating point.

The current simulation uses 30/360 US as a project convention, although the
reviewed contract excerpts do not distinguish US from European 30/360.
Prices, holdings, duration, and OAS are simulated; the constructed
benchmark is not a market index. Bond evidence remains incomplete.
