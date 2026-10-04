# High-Yield Portfolio Performance and Risk Analytics

## Purpose
Produce and defend a reconciled monthly portfolio report from
bond holdings data, while strengthening practical understanding
of fixed-income valuation, returns, and risk exposures.

## Business question
What drove portfolio return and benchmark-relative performance
over one month, and how did portfolio exposures differ from
the constructed benchmark?

## Scope
- Ten actual USD fixed-rate corporate bonds across five sectors.
- Primarily BB and B rating buckets.
- Beginning snapshot: March 31, 2026.
- Ending snapshot: April 30, 2026.
- Fixed face amounts; no trades, defaults, redemptions, or external flows.
- Include at least one scheduled coupon payment.
- Complete within two intensive days.

## Data approach
- Verify contractual terms from SEC filings or issuer documents.
- Use hypothetical portfolio allocations.
- Clearly label simulated clean prices, effective duration, and OAS.
- Use dated, sourced issue ratings where readily available;
  otherwise label assigned rating buckets as simulated.
- Calculate accrued interest and coupon cash from verified terms.
- Record field-level provenance and distinguish verified,
  simulated, calculated, and assigned fields.
- Limit bond sourcing to two hours; replace difficult candidates.
- This is a simulation, not actual April 2026 market performance
  or any investment firm's portfolio.

## Portfolio and benchmark
- Set unequal portfolio beginning weights under a documented
  hypothetical mandate before generating ending prices.
- Construct a benchmark using the same ten bonds, each with
  10% of beginning dirty market value.
- Fix face amounts after establishing beginning allocations.
- Allow weights to drift; do not rebalance.
- Use identical bond observations in both portfolios.
- Active performance therefore reflects beginning weight differences.
- The benchmark is not a market index.

## Valuation and return conventions
- Quantity means USD face amount.
- Clean price and accrued interest are per $100 face.
- Dirty market value = face amount / 100 ×
  (clean price + accrued interest).
- Snapshots are end-of-day, after payments occurring that day.
- Include coupon cash received in (beginning date, ending date].
- Beginning cash is zero.
- Retain coupon cash without reinvestment or interest.
- Ending NAV = ending dirty bond market value + coupon cash.
- Use each bond's verified contractual day-count convention.
- Ignore fees and taxes.

Bond total return:
(ending dirty value + coupon cash - beginning dirty value)
 / beginning dirty value

Price return:
(face amount / 100 × change in clean price)
 / beginning dirty value

Income return:
(face amount / 100 × change in accrued interest + coupon cash)
 / beginning dirty value

Beginning weight:
bond beginning dirty value / total beginning NAV

Holding contribution:
beginning weight × bond total return

Active contribution:
(portfolio beginning weight - benchmark beginning weight)
 × bond total return

## Risk measures
- Simulated effective duration, in years.
- Simulated option-adjusted spread (OAS), in basis points.
- Beginning and ending sector, rating, and issuer concentrations.
- Portfolio-minus-benchmark exposure differences.
- Weight duration and concentrations by total NAV;
  show cash separately with zero duration.
- Weight OAS by bond market value, excluding cash.
- Duration and OAS are supplied simulated inputs, not outputs
  from an option-pricing model.
- Do not claim causal rate/spread return attribution.

## Controls and acceptance criteria
- Detect duplicate identifiers within each snapshot.
- Detect missing required attributes and unmatched securities.
- Confirm fixed quantities and consistent holdings across dates.
- Recalculate and reconcile supplied market values.
- Confirm weights total 100%, including ending cash.
- Flag unusual clean-price movements for review.
- Reconcile price plus income return to total return.
- Reconcile holding contributions to portfolio return.
- Reconcile active contributions to portfolio-minus-benchmark return.
- Document deliberately introduced data errors and their resolution.
- Resolve exceptions or explicitly exclude affected records,
  disclosing the effect on scope and totals.
- Set numerical tolerances before running final checks.

## Tools
- PostgreSQL with pgAdmin: tables and validation queries.
- Python in VS Code: calculations, reconciliation, and plotting.
- Copilot: implementation support after formulas are understood.

## Deliverables
1. Holdings and benchmark files, provenance, and data dictionary.
2. SQL tables/views and data-quality exception records.
3. One Python script or notebook producing reconciled outputs.
4. One polished static dashboard.
5. One-page portfolio-manager note.
6. README documenting workflow, assumptions, and validation.

## Relationship to existing work
High-Yield Credit Analytics covers aggregate credit-market
monitoring and EBP research. This project covers individual
holdings, portfolio performance, benchmark comparison,
risk exposures, and data controls.

## Exclusions
No optimization, machine learning, live pricing APIs,
transaction accounting, key-rate duration, full yield-curve
modeling, derivatives, scenario engines, or production orchestration.
Record potential enhancements as future work.
