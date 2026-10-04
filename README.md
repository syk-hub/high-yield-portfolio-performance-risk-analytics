# High-Yield Portfolio Performance and Risk Analytics

This repository contains a simulated teaching workflow for calculating
bond returns, portfolio contributions, a constructed same-universe
benchmark, and risk exposures for March 31 through April 30, 2026.
It is not actual market performance or investment advice.

## Current inputs

- `bond_candidates.csv`: documented bond terms, source links, rating scope,
  and unresolved evidence checks.
- `simulated_prices.csv`: simulated beginning and ending clean prices.
- `portfolio_holdings.csv`: simulated teaching face allocations.
- `simulated_risk_inputs.csv`: illustrative duration and OAS inputs held
  constant across both valuation dates.
- `BOND_RESEARCH.md`: source notes, conventions, allocation rationale,
  simulated results, and outstanding evidence limitations.

The allocations were selected after inspection of simulated bond returns,
so results are illustrative and do not demonstrate investment selection
skill. Effective-duration and OAS values are broadly illustrative teaching
assumptions, not market observations, model-derived values, or measures
calibrated to these specific securities. Several bonds still have
unresolved evidence checks, including missing identifiers or dated ratings,
unconfirmed or inconsistent identifiers/terms, incomplete call details,
and outstanding-principal activity not verified through the end of April.
See `BOND_RESEARCH.md` and the candidate-level `unresolved_checks` field.

## Calculation scripts and execution order

Run from the repository root, using the selected Python environment:

```powershell
python .\calculate_bond_returns.py
python .\calculate_portfolio_returns.py
python .\calculate_risk_exposures.py
```

1. `calculate_bond_returns.py` computes accrued interest, coupon cash,
   dirty prices, and simulated bond returns using the documented project
   convention of 30/360 US.
2. `calculate_portfolio_returns.py` reuses the bond-return functions,
   calculates portfolio and constructed same-universe benchmark returns,
   validates contribution reconciliations, and saves return outputs.
3. `calculate_risk_exposures.py` reuses the valuation functions, calculates
   portfolio and benchmark duration/OAS exposures at both dates, and saves
   the risk summary.

The scripts use end-of-day valuations after coupon payments, assume zero
beginning cash, fixed face amounts, and coupon cash retained at zero
interest. The benchmark assigns equal beginning dirty-market-value weights
to the same ten bonds; it is not a market index.

## Current outputs

The two portfolio/risk scripts create or update `outputs/`:

- `bond_returns.csv`
- `portfolio_contributions.csv`
- `active_contributions.csv`
- `performance_summary.csv`
- `risk_exposure_summary.csv`
- `README.md`, which labels the exports as simulated

Returns, weights, and risk exposures are represented with explicit units
in their column names and stored at calculation precision where applicable.

## Pending work

- Adapt the SQL schema and validation queries to the current inputs and
  output conventions before using them.
- Dashboard work is pending; the legacy generator and dashboard artifacts
  have been retired.

`requirements.txt` is preserved from the original workflow. The current
calculation scripts use only the Python standard library.
