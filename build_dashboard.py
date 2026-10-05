"""Build a self-contained dashboard from the project's saved CSV inputs/outputs."""

from __future__ import annotations

import csv
import html
import math
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = ROOT / "outputs" / "portfolio_dashboard.html"
DATES = ("2026-03-31", "2026-04-30")
EXPECTED_BONDS = 10
EXPECTED_METRICS = {
    "beginning_nav",
    "ending_dirty_bond_value",
    "coupon_cash",
    "ending_nav",
    "portfolio_return",
    "benchmark_return",
    "active_return",
}

REQUIRED_COLUMNS = {
    "inputs/bond_candidates.csv": {"internal_id", "legal_issuer"},
    "inputs/portfolio_holdings.csv": {"internal_id", "face_value_usd"},
    "inputs/simulated_prices.csv": {
        "internal_id", "valuation_date", "clean_price", "price_status",
    },
    "inputs/simulated_risk_inputs.csv": {
        "internal_id", "valuation_date", "effective_duration_years",
        "oas_bps", "risk_status",
    },
    "outputs/bond_returns.csv": {
        "internal_id", "beginning_ai_usd_per_100_face",
        "ending_ai_usd_per_100_face", "coupon_cash_usd_per_100_face",
        "beginning_dirty_price_usd_per_100_face",
        "ending_dirty_price_usd_per_100_face", "price_return_decimal",
        "income_return_decimal", "total_return_decimal", "result_status",
    },
    "outputs/portfolio_contributions.csv": {
        "internal_id", "face_value_usd", "beginning_dirty_market_value_usd",
        "ending_dirty_market_value_usd", "coupon_cash_usd",
        "beginning_weight_decimal",
        "price_contribution_decimal", "income_contribution_decimal",
        "total_contribution_decimal", "result_status",
    },
    "outputs/active_contributions.csv": {
        "internal_id", "portfolio_beginning_weight_decimal",
        "benchmark_beginning_weight_decimal", "active_weight_decimal",
        "bond_total_return_decimal", "active_contribution_decimal",
        "result_status",
    },
    "outputs/performance_summary.csv": {
        "metric", "value", "unit", "result_status",
    },
    "outputs/risk_exposure_summary.csv": {
        "portfolio_or_benchmark", "valuation_date",
        "dirty_bond_market_value_usd", "cash_usd", "nav_usd",
        "cash_weight_decimal", "effective_duration_years",
        "average_bond_oas_bps", "risk_status",
    },
}


class DashboardDataError(ValueError):
    """Raised when saved CSV data cannot safely populate the dashboard."""


def read_csv(relative_path: str) -> list[dict[str, str]]:
    path = ROOT / relative_path
    if not path.is_file():
        raise DashboardDataError(f"Required CSV is missing: {relative_path}")
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            actual_columns = set(reader.fieldnames or ())
            missing_columns = REQUIRED_COLUMNS[relative_path] - actual_columns
            if missing_columns:
                missing = ", ".join(sorted(missing_columns))
                raise DashboardDataError(
                    f"{relative_path} is missing required columns: {missing}"
                )
            rows = list(reader)
    except (OSError, csv.Error) as exc:
        raise DashboardDataError(f"Could not read {relative_path}: {exc}") from exc
    if not rows:
        raise DashboardDataError(f"Required CSV contains no data rows: {relative_path}")
    return rows


def decimal_value(row: dict[str, str], column: str, source: str) -> Decimal:
    raw_value = row.get(column, "")
    if raw_value is None or not raw_value.strip():
        raise DashboardDataError(f"{source}: missing numeric value in {column}")
    try:
        value = Decimal(raw_value.strip())
    except InvalidOperation as exc:
        raise DashboardDataError(
            f"{source}: invalid numeric value for {column}: {raw_value!r}"
        ) from exc
    if not value.is_finite():
        raise DashboardDataError(
            f"{source}: non-finite numeric value for {column}: {raw_value!r}"
        )
    return value


def verify_unique_ids(
    rows: list[dict[str, str]], source: str, expected_ids: set[str]
) -> None:
    ids = [row["internal_id"].strip() for row in rows]
    if any(not internal_id for internal_id in ids):
        raise DashboardDataError(f"{source}: blank internal_id found")
    if len(ids) != len(set(ids)):
        raise DashboardDataError(f"{source}: duplicate internal_id found")
    if set(ids) != expected_ids:
        missing = sorted(expected_ids - set(ids))
        unexpected = sorted(set(ids) - expected_ids)
        raise DashboardDataError(
            f"{source}: internal_id coverage mismatch; "
            f"missing={missing}, unexpected={unexpected}"
        )


def validate_status(
    rows: Iterable[dict[str, str]], column: str, expected: str, source: str
) -> None:
    bad_rows = [
        str(index)
        for index, row in enumerate(rows, start=2)
        if row.get(column, "").strip() != expected
    ]
    if bad_rows:
        raise DashboardDataError(
            f"{source}: {column} must be {expected!r}; invalid CSV rows "
            f"{', '.join(bad_rows)}"
        )


def validate_numeric_columns(
    rows: list[dict[str, str]], columns: Iterable[str], source: str
) -> None:
    for index, row in enumerate(rows, start=2):
        for column in columns:
            decimal_value(row, column, f"{source} row {index}")


def exact_pairs(
    rows: list[dict[str, str]], source: str, expected_ids: set[str]
) -> None:
    pairs = [(row["internal_id"].strip(), row["valuation_date"].strip()) for row in rows]
    expected = {(internal_id, date) for internal_id in expected_ids for date in DATES}
    if len(pairs) != len(set(pairs)):
        raise DashboardDataError(f"{source}: duplicate bond/date row found")
    if set(pairs) != expected:
        missing = sorted(expected - set(pairs))
        unexpected = sorted(set(pairs) - expected)
        raise DashboardDataError(
            f"{source}: expected exactly ten bonds at both valuation dates; "
            f"missing={missing}, unexpected={unexpected}"
        )


def load_and_validate() -> dict[str, object]:
    inputs = {
        name: read_csv(name)
        for name in (
            "inputs/bond_candidates.csv",
            "inputs/portfolio_holdings.csv",
            "inputs/simulated_prices.csv",
            "inputs/simulated_risk_inputs.csv",
        )
    }
    outputs = {
        name: read_csv(name)
        for name in (
            "outputs/bond_returns.csv",
            "outputs/portfolio_contributions.csv",
            "outputs/active_contributions.csv",
            "outputs/performance_summary.csv",
            "outputs/risk_exposure_summary.csv",
        )
    }

    candidates = inputs["inputs/bond_candidates.csv"]
    candidate_ids = [row["internal_id"].strip() for row in candidates]
    if len(candidate_ids) != EXPECTED_BONDS or len(set(candidate_ids)) != EXPECTED_BONDS:
        raise DashboardDataError(
            f"inputs/bond_candidates.csv must contain exactly "
            f"{EXPECTED_BONDS} unique bonds"
        )
    if any(not row["legal_issuer"].strip() for row in candidates):
        raise DashboardDataError(
            "inputs/bond_candidates.csv contains a blank legal_issuer"
        )
    expected_ids = set(candidate_ids)
    issuers = {
        row["internal_id"].strip(): row["legal_issuer"].strip()
        for row in candidates
    }

    holdings = inputs["inputs/portfolio_holdings.csv"]
    verify_unique_ids(holdings, "inputs/portfolio_holdings.csv", expected_ids)
    validate_numeric_columns(
        holdings, ("face_value_usd",), "inputs/portfolio_holdings.csv"
    )
    if any(
        decimal_value(row, "face_value_usd", "inputs/portfolio_holdings.csv") <= 0
        for row in holdings
    ):
        raise DashboardDataError(
            "inputs/portfolio_holdings.csv contains a non-positive face value"
        )

    prices = inputs["inputs/simulated_prices.csv"]
    exact_pairs(prices, "inputs/simulated_prices.csv", expected_ids)
    validate_numeric_columns(
        prices, ("clean_price",), "inputs/simulated_prices.csv"
    )
    validate_status(
        prices, "price_status", "simulated", "inputs/simulated_prices.csv"
    )
    if any(
        decimal_value(row, "clean_price", "inputs/simulated_prices.csv") <= 0
        for row in prices
    ):
        raise DashboardDataError(
            "inputs/simulated_prices.csv contains a non-positive clean price"
        )

    risk_inputs = inputs["inputs/simulated_risk_inputs.csv"]
    exact_pairs(risk_inputs, "inputs/simulated_risk_inputs.csv", expected_ids)
    validate_numeric_columns(
        risk_inputs, ("effective_duration_years", "oas_bps"),
        "inputs/simulated_risk_inputs.csv",
    )
    validate_status(
        risk_inputs, "risk_status", "simulated",
        "inputs/simulated_risk_inputs.csv",
    )
    for row in risk_inputs:
        duration = decimal_value(
            row, "effective_duration_years", "inputs/simulated_risk_inputs.csv"
        )
        oas = decimal_value(row, "oas_bps", "inputs/simulated_risk_inputs.csv")
        if duration <= 0 or oas < 0:
            raise DashboardDataError(
                "inputs/simulated_risk_inputs.csv contains an invalid duration "
                "or OAS"
            )

    bond_returns = outputs["outputs/bond_returns.csv"]
    portfolio_contributions = outputs["outputs/portfolio_contributions.csv"]
    active_contributions = outputs["outputs/active_contributions.csv"]
    for rows, source in (
        (bond_returns, "outputs/bond_returns.csv"),
        (portfolio_contributions, "outputs/portfolio_contributions.csv"),
        (active_contributions, "outputs/active_contributions.csv"),
    ):
        verify_unique_ids(rows, source, expected_ids)
        validate_status(rows, "result_status", "simulated", source)

    validate_numeric_columns(
        bond_returns,
        (
            "beginning_ai_usd_per_100_face",
            "ending_ai_usd_per_100_face",
            "coupon_cash_usd_per_100_face",
            "beginning_dirty_price_usd_per_100_face",
            "ending_dirty_price_usd_per_100_face",
            "price_return_decimal", "income_return_decimal",
            "total_return_decimal",
        ),
        "outputs/bond_returns.csv",
    )
    validate_numeric_columns(
        portfolio_contributions,
        (
            "face_value_usd", "beginning_dirty_market_value_usd",
            "ending_dirty_market_value_usd", "coupon_cash_usd",
            "beginning_weight_decimal", "price_contribution_decimal",
            "income_contribution_decimal", "total_contribution_decimal",
        ),
        "outputs/portfolio_contributions.csv",
    )
    validate_numeric_columns(
        active_contributions,
        (
            "portfolio_beginning_weight_decimal",
            "benchmark_beginning_weight_decimal", "active_weight_decimal",
            "bond_total_return_decimal", "active_contribution_decimal",
        ),
        "outputs/active_contributions.csv",
    )

    performance_rows = outputs["outputs/performance_summary.csv"]
    performance: dict[str, Decimal] = {}
    for row in performance_rows:
        metric = row["metric"].strip()
        if metric in performance:
            raise DashboardDataError(
                f"outputs/performance_summary.csv contains duplicate metric {metric!r}"
            )
        performance[metric] = decimal_value(
            row, "value", "outputs/performance_summary.csv"
        )
        if row["result_status"].strip() != "simulated":
            raise DashboardDataError(
                f"outputs/performance_summary.csv metric {metric!r} "
                "does not have simulated status"
            )
    if set(performance) != EXPECTED_METRICS:
        raise DashboardDataError(
            "outputs/performance_summary.csv metric coverage mismatch; "
            f"expected={sorted(EXPECTED_METRICS)}, found={sorted(performance)}"
        )

    risk_summary = outputs["outputs/risk_exposure_summary.csv"]
    risk_keys = [
        (row["portfolio_or_benchmark"].strip(), row["valuation_date"].strip())
        for row in risk_summary
    ]
    expected_risk_keys = {
        (portfolio_type, date)
        for portfolio_type in ("portfolio", "constructed_benchmark")
        for date in DATES
    }
    if len(risk_keys) != len(set(risk_keys)) or set(risk_keys) != expected_risk_keys:
        raise DashboardDataError(
            "outputs/risk_exposure_summary.csv must contain exactly one row "
            "for each portfolio/benchmark and valuation date"
        )
    validate_status(
        risk_summary, "risk_status", "simulated",
        "outputs/risk_exposure_summary.csv",
    )
    validate_numeric_columns(
        risk_summary,
        (
            "dirty_bond_market_value_usd", "cash_usd", "nav_usd",
            "cash_weight_decimal", "effective_duration_years",
            "average_bond_oas_bps",
        ),
        "outputs/risk_exposure_summary.csv",
    )

    summary_by_id = {
        row["internal_id"].strip(): row for row in portfolio_contributions
    }
    returns_by_id = {row["internal_id"].strip(): row for row in bond_returns}
    active_by_id = {row["internal_id"].strip(): row for row in active_contributions}
    risk_by_key = {
        (row["portfolio_or_benchmark"].strip(), row["valuation_date"].strip()): row
        for row in risk_summary
    }
    return {
        "issuers": issuers,
        "ids": candidate_ids,
        "portfolio": performance,
        "contributions": summary_by_id,
        "returns": returns_by_id,
        "active": active_by_id,
        "risk": risk_by_key,
    }


def number(value: Decimal | str) -> float:
    converted = float(value)
    if not math.isfinite(converted):
        raise DashboardDataError(f"Numeric value cannot be represented for chart: {value}")
    return converted


def fmt_decimal_percent(value: Decimal, places: int = 2) -> str:
    return f"{value * 100:,.{places}f}%"


def fmt_usd(value: Decimal) -> str:
    return f"${value:,.2f}"


def svg_axis_ticks(
    minimum: float, maximum: float, count: int = 5
) -> tuple[list[float], float, float]:
    if minimum == maximum:
        minimum -= 1
        maximum += 1
    rough_step = (maximum - minimum) / (count - 1)
    magnitude = 10 ** math.floor(math.log10(rough_step))
    normalized_step = rough_step / magnitude
    if normalized_step <= 1:
        step_factor = 1
    elif normalized_step <= 2:
        step_factor = 2
    elif normalized_step <= 2.5:
        step_factor = 2.5
    elif normalized_step <= 5:
        step_factor = 5
    else:
        step_factor = 10
    step = step_factor * magnitude
    axis_minimum = math.floor(minimum / step) * step
    axis_maximum = math.ceil(maximum / step) * step
    if axis_minimum == axis_maximum:
        axis_minimum -= step
        axis_maximum += step
    first_multiple = math.ceil(axis_minimum / step)
    last_multiple = math.floor(axis_maximum / step)
    ticks = [multiple * step for multiple in range(first_multiple, last_multiple + 1)]
    if not any(math.isclose(tick, 0, abs_tol=step * 1e-12) for tick in ticks):
        ticks.append(0.0)
        ticks.sort()
    return ticks, axis_minimum, axis_maximum


def contribution_chart(
    ids: list[str],
    issuers: dict[str, str],
    contributions: dict[str, dict[str, str]],
) -> str:
    series = [
        ("Price", "price_contribution_decimal", "#3976a8"),
        ("Income", "income_contribution_decimal", "#26917f"),
    ]
    points = [
        number(Decimal(contributions[internal_id][column]) * 100)
        for internal_id in ids
        for _, column, _ in series
    ]
    low, high = min(0.0, min(points)), max(0.0, max(points))
    span = max(high - low, 0.1)
    low -= span * 0.12
    high += span * 0.12
    ticks, low, high = svg_axis_ticks(low, high)
    width, left, right = 1120, 300, 1080
    plot_width = right - left
    row_height, top, bottom = 48, 34, 36 + 34 + len(ids) * 48
    height = bottom + 44
    x = lambda value: left + (value - low) / (high - low) * plot_width
    zero_x = x(0)
    output = [
        f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" '
        'aria-label="Horizontal price and income contribution chart in percentage points">',
        '<title>Portfolio contribution by bond, in percentage points</title>',
    ]
    for tick in ticks:
        tick_x = x(tick)
        output.append(
            f'<line x1="{tick_x:.2f}" y1="{top}" x2="{tick_x:.2f}" y2="{bottom}" '
            'class="grid-line"/>'
        )
        output.append(
            f'<text x="{tick_x:.2f}" y="{height - 14}" class="axis-label" '
            f'text-anchor="middle">{tick:g}</text>'
        )
    output.append(
        f'<line x1="{zero_x:.2f}" y1="{top}" x2="{zero_x:.2f}" y2="{bottom}" '
        'class="zero-line"/>'
    )
    for index, internal_id in enumerate(ids):
        issuer = issuers[internal_id]
        short_name = issuer if len(issuer) <= 34 else issuer[:31].rstrip() + "..."
        center = top + 24 + index * row_height
        output.append(
            f'<text x="{left - 16}" y="{center + 4}" class="bond-label" '
            f'text-anchor="end"><title>{html.escape(issuer)}</title>'
            f'{html.escape(short_name)}</text>'
        )
        for series_index, (label, column, color) in enumerate(series):
            value = number(Decimal(contributions[internal_id][column]) * 100)
            bar_y = center - 12 + series_index * 15
            end_x = x(value)
            bar_x, bar_width = min(zero_x, end_x), abs(end_x - zero_x)
            tooltip = (
                f"{issuer} — {label.lower()} contribution: {value:.4f} "
                "percentage points"
            )
            output.append(
                f'<rect x="{bar_x:.2f}" y="{bar_y}" width="{bar_width:.2f}" '
                f'height="9" rx="4.5" fill="{color}"><title>'
                f'{html.escape(tooltip)}</title></rect>'
            )
    output.append(f'<text x="{(left + right) / 2}" y="{height - 1}" class="axis-title" text-anchor="middle">Contribution (percentage points)</text>')
    output.append("</svg>")
    return "".join(output)


def active_chart(
    ids: list[str],
    issuers: dict[str, str],
    active: dict[str, dict[str, str]],
) -> str:
    values = [
        number(Decimal(active[internal_id]["active_contribution_decimal"]) * 10000)
        for internal_id in ids
    ]
    low, high = min(0.0, min(values)), max(0.0, max(values))
    span = max(high - low, 1.0)
    low -= span * 0.12
    high += span * 0.12
    ticks, low, high = svg_axis_ticks(low, high)
    width, left, right = 1120, 300, 1080
    plot_width = right - left
    row_height, top = 42, 34
    bottom = top + len(ids) * row_height
    height = bottom + 50
    x = lambda value: left + (value - low) / (high - low) * plot_width
    zero_x = x(0)
    output = [
        f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" '
        'aria-label="Horizontal active contribution chart in basis points">',
        '<title>Active contribution by bond, in basis points</title>',
    ]
    for tick in ticks:
        tick_x = x(tick)
        output.append(
            f'<line x1="{tick_x:.2f}" y1="{top}" x2="{tick_x:.2f}" y2="{bottom}" '
            'class="grid-line"/>'
        )
        output.append(
            f'<text x="{tick_x:.2f}" y="{height - 17}" class="axis-label" '
            f'text-anchor="middle">{tick:g}</text>'
        )
    output.append(
        f'<line x1="{zero_x:.2f}" y1="{top}" x2="{zero_x:.2f}" y2="{bottom}" '
        'class="zero-line"/>'
    )
    for index, internal_id in enumerate(ids):
        issuer = issuers[internal_id]
        short_name = issuer if len(issuer) <= 34 else issuer[:31].rstrip() + "..."
        value = values[index]
        bar_y = top + 8 + index * row_height
        end_x = x(value)
        bar_x, bar_width = min(zero_x, end_x), abs(end_x - zero_x)
        tooltip = f"{issuer} — active contribution: {value:.4f} basis points"
        output.append(
            f'<text x="{left - 16}" y="{bar_y + 11}" class="bond-label" '
            f'text-anchor="end"><title>{html.escape(issuer)}</title>'
            f'{html.escape(short_name)}</text>'
        )
        output.append(
            f'<rect x="{bar_x:.2f}" y="{bar_y}" width="{bar_width:.2f}" '
            f'height="15" rx="7.5" fill="#c27b3a"><title>'
            f'{html.escape(tooltip)}</title></rect>'
        )
    output.append(f'<text x="{(left + right) / 2}" y="{height - 1}" class="axis-title" text-anchor="middle">Active contribution (basis points)</text>')
    output.append("</svg>")
    return "".join(output)


def risk_table(risk: dict[tuple[str, str], dict[str, str]]) -> str:
    body = []
    for date in DATES:
        display_date = "March 31, 2026" if date == DATES[0] else "April 30, 2026"
        for portfolio_type, label in (
            ("portfolio", "Portfolio"),
            ("constructed_benchmark", "Constructed benchmark"),
        ):
            row = risk[(portfolio_type, date)]
            body.append(
                "<tr>"
                f"<th scope=\"row\">{display_date}</th>"
                f"<td>{label}</td>"
                f"<td>{Decimal(row['effective_duration_years']):,.3f} years</td>"
                f"<td>{Decimal(row['average_bond_oas_bps']):,.1f} bps</td>"
                f"<td>{Decimal(row['cash_weight_decimal']) * 100:,.2f}%</td>"
                "</tr>"
            )
    return "".join(body)


def holdings_table(
    ids: list[str],
    issuers: dict[str, str],
    contributions: dict[str, dict[str, str]],
    returns: dict[str, dict[str, str]],
    active: dict[str, dict[str, str]],
) -> str:
    body = []
    for internal_id in ids:
        row = contributions[internal_id]
        bond_return = returns[internal_id]
        active_row = active[internal_id]
        body.append(
            "<tr>"
            f"<th scope=\"row\"><span title=\"{html.escape(internal_id)}\">"
            f"{html.escape(issuers[internal_id])}</span></th>"
            f"<td>{Decimal(row['beginning_weight_decimal']) * 100:,.2f}%</td>"
            f"<td>{Decimal(bond_return['total_return_decimal']) * 100:,.2f}%</td>"
            f"<td>{Decimal(row['total_contribution_decimal']) * 100:,.3f} pp</td>"
            f"<td>{Decimal(active_row['active_contribution_decimal']) * 10000:,.2f} bps</td>"
            "</tr>"
        )
    return "".join(body)


def build_html(data: dict[str, object]) -> str:
    performance = data["portfolio"]
    issuers = data["issuers"]
    ids = data["ids"]
    contributions = data["contributions"]
    returns = data["returns"]
    active = data["active"]
    risk = data["risk"]

    kpis = (
        (
            "Portfolio return",
            fmt_decimal_percent(performance["portfolio_return"]),
            "Portfolio total return over the period, including price change, accrued interest, and coupon cash.",
            "simulated",
        ),
        (
            "Constructed benchmark return",
            fmt_decimal_percent(performance["benchmark_return"]),
            "Return on the constructed same-universe benchmark; it is not a market index.",
            "simulated",
        ),
        (
            "Active return",
            f"{performance['active_return'] * 10000:,.2f} bps",
            "Portfolio return minus constructed benchmark return. One basis point is 0.01 percentage point.",
            "simulated",
        ),
        (
            "Ending NAV",
            fmt_usd(performance["ending_nav"]),
            "Ending net asset value: ending dirty bond value plus retained coupon cash.",
            "simulated",
        ),
    )
    cards = "".join(
        f'<article class="kpi" title="{html.escape(tip)}">'
        f'<p class="kpi-label">{html.escape(label)}</p>'
        f'<p class="kpi-value">{html.escape(value)}</p>'
        f'<span class="kpi-status">{status}</span></article>'
        for label, value, tip, status in kpis
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>High-yield portfolio | Performance &amp; risk</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172a3b; --muted: #526879; --paper: #f8f5ed;
      --card: #fffefa; --line: #ded8ca; --navy: #102b43;
      --blue: #315f82; --teal: #087f70; --amber: #bd9142;
      --positive: #176a58; --negative: #a34437;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--paper); color: var(--ink);
      font: 16px/1.55 "Segoe UI", Arial, sans-serif; }}
    .shell {{ max-width: 1240px; margin: 0 auto; padding: 34px 26px 52px; }}
    .hero {{ padding: 30px 32px; background: var(--navy); color: #fff;
      border-radius: 18px; border-bottom: 4px solid var(--amber); }}
    .eyebrow {{ margin: 0 0 8px; text-transform: uppercase; letter-spacing: .12em;
      font-size: .76rem; font-weight: 700; color: #c7d6e2; }}
    h1 {{ margin: 0; color: #fff; font-size: clamp(1.85rem, 3.2vw, 2.8rem);
      line-height: 1.13; letter-spacing: .025em; font-weight: 800; }}
    .period {{ margin: 9px 0 0; color: #d4e0e8; }}
    .disclosure {{ margin: 18px 0 0; padding: 12px 15px; border-left: 4px solid #e4aa63;
      background: rgba(255,255,255,.09); border-radius: 4px 9px 9px 4px; }}
    .kpis {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 15px; margin: 20px 0; }}
    .kpi, .panel {{ background: var(--card); border: 1px solid var(--line);
      border-radius: 14px; box-shadow: 0 4px 16px rgba(24,44,61,.045); }}
    .kpi {{ padding: 19px 20px 17px; min-height: 132px;
      border-top: 3px solid var(--teal); }}
    .kpi-label {{ margin: 0; color: #40576a; font-size: .9rem; font-weight: 700; }}
    .kpi-value {{ margin: 8px 0 3px; color: var(--navy);
      font-size: clamp(1.55rem, 2.4vw, 2.1rem); font-weight: 800;
      letter-spacing: -.03em; font-variant-numeric: tabular-nums; }}
    .kpi-status {{ color: var(--muted); font-size: .72rem; text-transform: uppercase;
      letter-spacing: .09em; }}
    .panel {{ margin-top: 18px; padding: 22px 22px 20px; }}
    .panel h2 {{ margin: 0; color: var(--navy); font-size: 1.26rem;
      font-weight: 750; letter-spacing: -.01em; }}
    .panel-intro {{ margin: 5px 0 15px; color: var(--muted); font-size: .91rem; }}
    .chart-wrap {{ overflow-x: auto; }}
    .chart {{ display: block; width: 100%; min-width: 740px; height: auto; }}
    .grid-line {{ stroke: #e9e3d8; stroke-width: 1; }}
    .zero-line {{ stroke: #718395; stroke-width: 1.5; }}
    .axis-label {{ fill: #465d70; font: 12px "Segoe UI", Arial, sans-serif; }}
    .axis-title {{ fill: #30495d; font: 700 12px "Segoe UI", Arial, sans-serif; }}
    .bond-label {{ fill: #263e52; font: 12px "Segoe UI", Arial, sans-serif; }}
    .legend {{ display: flex; flex-wrap: wrap; gap: 18px; margin: 5px 0 0 9px;
      color: var(--muted); font-size: .85rem; }}
    .legend span {{ display: inline-flex; align-items: center; gap: 7px; }}
    .swatch {{ display: inline-block; width: 12px; height: 12px; border-radius: 3px; }}
    .table-wrap {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: .9rem; }}
    th, td {{ padding: 11px 12px; border-bottom: 1px solid var(--line);
      text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }}
    thead th {{ color: #203b50; background: #f1eee5; font-size: .8rem;
      font-weight: 750; letter-spacing: .035em; }}
    th:first-child, td:first-child {{ text-align: left; }}
    tbody th {{ font-weight: 600; }}
    tbody tr:last-child th, tbody tr:last-child td {{ border-bottom: 0; }}
    .risk-table th:nth-child(2), .risk-table td:nth-child(2) {{ text-align: left; }}
    .method {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
    .method p {{ margin: 8px 0 0; color: #4e6374; font-size: .91rem; }}
    .footnote {{ margin: 17px 4px 0; color: var(--muted); font-size: .8rem; }}
    abbr[title], [title] {{ text-decoration: none; }}
    .term {{ text-decoration: underline dotted; text-underline-offset: 3px; cursor: help; }}
    @media (max-width: 850px) {{
      .kpis {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 560px) {{
      .shell {{ padding: 15px 12px 32px; }}
      .hero {{ padding: 22px 18px; border-radius: 13px; }}
      .kpis {{ gap: 9px; margin: 12px 0; }}
      .kpi {{ padding: 13px; min-height: 112px; }}
      .kpi-value {{ font-size: 1.28rem; }}
      .panel {{ padding: 17px 14px; margin-top: 12px; }}
      .method {{ grid-template-columns: 1fr; gap: 12px; }}
    }}
    @media print {{
      body {{ background: #fff; }}
      .shell {{ max-width: none; padding: 0; }}
      .hero {{ print-color-adjust: exact; -webkit-print-color-adjust: exact; }}
      .panel, .kpi {{ box-shadow: none; break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <header class="hero">
      <p class="eyebrow">Simulated teaching portfolio</p>
      <h1>HIGH-YIELD PORTFOLIO PERFORMANCE &amp; RISK</h1>
      <p class="period">March 31–April 30, 2026</p>
      <p class="disclosure"><strong>Important disclosure:</strong> Bond terms are based on documented real-bond evidence. Prices, holdings, duration, and OAS are simulated. Bond eligibility evidence remains incomplete, including unresolved identifier, rating, call-term, and outstanding-principal checks. Results are illustrative, not actual market performance or investment advice.</p>
    </header>

    <section class="kpis" aria-label="Portfolio summary">{cards}</section>

    <section class="panel" aria-labelledby="contributions-title">
      <h2 id="contributions-title">Bond contribution: price and income</h2>
      <p class="panel-intro">Portfolio contribution components, shown in percentage points. Hover over a bar for its exact value. <span class="term" title="Price contribution is the bond's price-return component multiplied by its beginning portfolio weight.">Price contribution</span> and <span class="term" title="Income contribution includes coupon cash and accrued-interest change, weighted by the beginning portfolio weight.">income contribution</span> sum to each bond's total portfolio contribution.</p>
      <div class="chart-wrap">{contribution_chart(ids, issuers, contributions)}</div>
      <div class="legend" aria-label="Chart legend">
        <span><i class="swatch" style="background:#3976a8"></i>Price</span>
        <span><i class="swatch" style="background:#26917f"></i>Income</span>
      </div>
    </section>

    <section class="panel" aria-labelledby="active-title">
      <h2 id="active-title">Active contribution by bond</h2>
      <p class="panel-intro">Basis points of portfolio active return attributable to the difference between each portfolio weight and the benchmark's 10% beginning weight. Hover for exact values.</p>
      <div class="chart-wrap">{active_chart(ids, issuers, active)}</div>
    </section>

    <section class="panel" aria-labelledby="risk-title">
      <h2 id="risk-title">Portfolio and benchmark risk</h2>
      <p class="panel-intro">Risk observations at each valuation date. <span class="term" title="Effective duration measures price sensitivity to a parallel shift in the reference interest-rate curve, accounting for embedded options.">Effective duration</span> is shown in years; <span class="term" title="Average bond OAS is the market-value-weighted average option-adjusted spread across bonds, in basis points.">average bond OAS</span> is in basis points. Cash weight is retained coupon cash divided by NAV.</p>
      <div class="table-wrap">
        <table class="risk-table">
          <thead><tr><th scope="col">Valuation date</th><th scope="col">Portfolio</th><th scope="col" title="Sensitivity to a parallel shift in the reference interest-rate curve, accounting for embedded options; portfolio duration is market-value weighted.">Effective duration</th><th scope="col" title="Market-value-weighted average option-adjusted spread across bonds.">Average bond OAS</th><th scope="col" title="Retained coupon cash divided by NAV.">Cash weight</th></tr></thead>
          <tbody>{risk_table(risk)}</tbody>
        </table>
      </div>
    </section>

    <section class="panel" aria-labelledby="holdings-title">
      <h2 id="holdings-title">Bond holdings and contributions</h2>
      <p class="panel-intro">Returns and weights are percentages; portfolio contribution is in percentage points, and active contribution is in basis points.</p>
      <div class="table-wrap">
        <table>
          <thead><tr><th scope="col">Legal issuer</th><th scope="col" title="Beginning dirty market value divided by beginning portfolio NAV.">Beginning weight</th><th scope="col" title="Bond total return includes dirty-price movement and coupon cash, per $100 face.">Bond return</th><th scope="col" title="Beginning portfolio weight multiplied by the bond total return.">Portfolio contribution</th><th scope="col" title="Portfolio beginning weight minus benchmark beginning weight, multiplied by bond return.">Active contribution</th></tr></thead>
          <tbody>{holdings_table(ids, issuers, contributions, returns, active)}</tbody>
        </table>
      </div>
    </section>

    <section class="panel method" aria-labelledby="method-title">
      <div>
        <h2 id="method-title">Methodology</h2>
        <p><span class="term" title="Dirty price equals clean price plus accrued interest.">Dirty-price returns</span> include coupon cash; received coupons are retained as cash. The constructed benchmark has equal beginning dirty-market-value weights across the ten bonds and holds fixed face positions. Cash earns zero interest.</p>
      </div>
      <div>
        <h2>Interpretation</h2>
        <p>Portfolio allocations were selected after reviewing simulated returns. Duration and OAS are broad illustrative teaching inputs, not calibrated security-level market observations. Eligibility evidence and several bond-level checks remain unresolved; see the research documentation for details.</p>
      </div>
    </section>
    <p class="footnote">All figures are generated from the project's saved CSV results. Monetary values are USD. This self-contained page requires no server or external libraries.</p>
  </main>
</body>
</html>
"""


def main() -> int:
    try:
        data = load_and_validate()
        document = build_html(data)
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(document, encoding="utf-8", newline="\n")
    except (DashboardDataError, OSError) as exc:
        print(f"Dashboard build failed: {exc}", file=sys.stderr)
        return 1
    print(f"Dashboard written to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
