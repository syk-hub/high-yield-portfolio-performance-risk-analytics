"""Calculate simulated portfolio and constructed-benchmark risk exposures."""

import csv
from datetime import date
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path

from calculate_bond_returns import (
    BASE_DIR,
    END_DATE,
    START_DATE,
    calculate_bond_returns,
    read_candidates,
    read_prices,
)
from calculate_portfolio_returns import read_holdings


TOLERANCE = Decimal("1e-25")
VALUATION_DATES = (START_DATE, END_DATE)
RISK_FIELDS = {
    "internal_id",
    "valuation_date",
    "effective_duration_years",
    "oas_bps",
    "risk_status",
}


def read_risk_inputs(
    path: Path, candidate_ids: set[str]
) -> dict[tuple[str, date], tuple[Decimal, Decimal]]:
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None or not RISK_FIELDS.issubset(reader.fieldnames):
            raise ValueError(f"{path.name} is missing required columns: {sorted(RISK_FIELDS)}")

        risk_inputs: dict[tuple[str, date], tuple[Decimal, Decimal]] = {}
        for line_number, row in enumerate(reader, start=2):
            internal_id = (row.get("internal_id") or "").strip()
            if internal_id not in candidate_ids:
                raise ValueError(
                    f"{path.name} row {line_number}: unknown internal_id {internal_id!r}"
                )
            try:
                valuation_date = date.fromisoformat(row["valuation_date"])
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"{path.name} row {line_number}: invalid valuation_date "
                    f"{row.get('valuation_date')!r}"
                ) from error
            if valuation_date not in VALUATION_DATES:
                raise ValueError(
                    f"{path.name} row {line_number}: unexpected valuation date "
                    f"{valuation_date.isoformat()}"
                )
            key = (internal_id, valuation_date)
            if key in risk_inputs:
                raise ValueError(
                    f"{path.name} row {line_number}: duplicate risk input "
                    f"{internal_id} {valuation_date.isoformat()}"
                )
            try:
                duration = Decimal(row["effective_duration_years"])
                oas = Decimal(row["oas_bps"])
            except (InvalidOperation, TypeError) as error:
                raise ValueError(
                    f"{path.name} row {line_number}: duration and OAS must be numeric"
                ) from error
            if not duration.is_finite() or duration <= 0:
                raise ValueError(
                    f"{path.name} row {line_number}: effective duration must be "
                    f"finite and positive, got {duration}"
                )
            if not oas.is_finite() or oas < 0:
                raise ValueError(
                    f"{path.name} row {line_number}: OAS must be finite and "
                    f"nonnegative, got {oas}"
                )
            if (row.get("risk_status") or "").strip() != "simulated":
                raise ValueError(
                    f"{path.name} row {line_number}: risk_status must be simulated"
                )
            risk_inputs[key] = (duration, oas)

    expected = {
        (internal_id, valuation_date)
        for internal_id in candidate_ids
        for valuation_date in VALUATION_DATES
    }
    missing = expected - risk_inputs.keys()
    if missing:
        details = ", ".join(
            f"{internal_id}@{valuation_date.isoformat()}"
            for internal_id, valuation_date in sorted(missing)
        )
        raise ValueError(f"{path.name} is missing required risk inputs: {details}")
    if len(risk_inputs) != len(expected):
        raise ValueError(f"{path.name} must contain exactly one row per candidate/date pair")
    return risk_inputs


def decimal_text(value: Decimal) -> str:
    return format(value, "f")


def write_summary(path: Path, rows: list[dict[str, str]]) -> None:
    fields = [
        "portfolio_or_benchmark",
        "valuation_date",
        "dirty_bond_market_value_usd",
        "cash_usd",
        "nav_usd",
        "cash_weight_decimal",
        "effective_duration_years",
        "average_bond_oas_bps",
        "risk_status",
    ]
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def calculate_exposure(
    label: str,
    valuation_date: date,
    face_values: dict[str, Decimal],
    bond_returns: dict,
    risk_inputs: dict[tuple[str, date], tuple[Decimal, Decimal]],
) -> dict[str, Decimal]:
    dirty_market_value = Decimal(0)
    cash = Decimal(0)
    duration_value = Decimal(0)
    oas_value = Decimal(0)

    for internal_id, face_value in face_values.items():
        result = bond_returns[internal_id]
        if valuation_date == START_DATE:
            dirty_price = result.beginning_dirty
        elif valuation_date == END_DATE:
            dirty_price = result.ending_dirty
        else:
            raise ValueError(f"Unsupported valuation date: {valuation_date}")

        market_value = face_value / Decimal(100) * dirty_price
        dirty_market_value += market_value
        duration, oas = risk_inputs[(internal_id, valuation_date)]
        duration_value += market_value * duration
        oas_value += market_value * oas
        if valuation_date == END_DATE:
            cash += face_value / Decimal(100) * result.coupon_cash

    nav = dirty_market_value + cash
    if dirty_market_value <= 0 or nav <= 0:
        raise ValueError(f"{label} has nonpositive dirty bond value or NAV")
    return {
        "dirty_bond_market_value_usd": dirty_market_value,
        "cash_usd": cash,
        "nav_usd": nav,
        "cash_weight_decimal": cash / nav,
        "effective_duration_years": duration_value / nav,
        "average_bond_oas_bps": oas_value / dirty_market_value,
    }


def main() -> None:
    with localcontext() as context:
        context.prec = 50
        candidates = read_candidates(BASE_DIR / "bond_candidates.csv")
        candidate_ids = set(candidates)
        prices = read_prices(BASE_DIR / "simulated_prices.csv", candidate_ids)
        holdings = read_holdings(BASE_DIR / "portfolio_holdings.csv", candidate_ids)
        risk_inputs = read_risk_inputs(
            BASE_DIR / "simulated_risk_inputs.csv", candidate_ids
        )
        bond_returns = calculate_bond_returns(candidates, prices)
        if len(candidate_ids) != 10:
            raise ValueError("Constructed benchmark requires exactly ten candidate bonds")

        beginning_portfolio = calculate_exposure(
            "portfolio", START_DATE, holdings, bond_returns, risk_inputs
        )
        benchmark_face_values = {
            internal_id: (
                beginning_portfolio["nav_usd"]
                / Decimal(10)
                * Decimal(100)
                / bond_returns[internal_id].beginning_dirty
            )
            for internal_id in candidates
        }

        output_rows: list[dict[str, str]] = []
        exposure_results: dict[tuple[str, date], dict[str, Decimal]] = {}
        for label, face_values in (
            ("portfolio", holdings),
            ("constructed_benchmark", benchmark_face_values),
        ):
            for valuation_date in VALUATION_DATES:
                exposure = calculate_exposure(
                    label, valuation_date, face_values, bond_returns, risk_inputs
                )
                bond_nav_weight = exposure["dirty_bond_market_value_usd"] / exposure[
                    "nav_usd"
                ]
                if abs(bond_nav_weight + exposure["cash_weight_decimal"] - Decimal(1)) > TOLERANCE:
                    raise AssertionError(
                        f"{label} NAV weights do not sum to 1 on {valuation_date}"
                    )
                exposure_results[(label, valuation_date)] = exposure
                output_rows.append(
                    {
                        "portfolio_or_benchmark": label,
                        "valuation_date": valuation_date.isoformat(),
                        "dirty_bond_market_value_usd": decimal_text(
                            exposure["dirty_bond_market_value_usd"]
                        ),
                        "cash_usd": decimal_text(exposure["cash_usd"]),
                        "nav_usd": decimal_text(exposure["nav_usd"]),
                        "cash_weight_decimal": decimal_text(
                            exposure["cash_weight_decimal"]
                        ),
                        "effective_duration_years": decimal_text(
                            exposure["effective_duration_years"]
                        ),
                        "average_bond_oas_bps": decimal_text(
                            exposure["average_bond_oas_bps"]
                        ),
                        "risk_status": "simulated",
                    }
                )

        simple_average_duration = sum(
            (
                risk_inputs[(internal_id, START_DATE)][0]
                for internal_id in candidates
            ),
            Decimal(0),
        ) / Decimal(10)
        simple_average_oas = sum(
            (
                risk_inputs[(internal_id, START_DATE)][1]
                for internal_id in candidates
            ),
            Decimal(0),
        ) / Decimal(10)
        benchmark_beginning = exposure_results[("constructed_benchmark", START_DATE)]
        if abs(
            benchmark_beginning["effective_duration_years"] - simple_average_duration
        ) > TOLERANCE:
            raise AssertionError(
                "Benchmark beginning duration does not equal simple average of inputs"
            )
        if abs(benchmark_beginning["average_bond_oas_bps"] - simple_average_oas) > TOLERANCE:
            raise AssertionError(
                "Benchmark beginning OAS does not equal simple average of inputs"
            )

        output_path = BASE_DIR / "outputs" / "risk_exposure_summary.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        write_summary(output_path, output_rows)

        print(
            "Simulated risk inputs are teaching assumptions. Benchmark is constructed "
            "with equal beginning dirty-market-value allocations; all benchmark face "
            "amounts remain fixed, and coupon cash earns zero interest."
        )
        print()
        print(
            f"{'portfolio_or_benchmark':<25} {'valuation_date':<12} "
            f"{'dirty bond MV (USD)':>22} {'cash (USD)':>16} {'NAV (USD)':>18} "
            f"{'cash weight':>14} {'duration (years)':>18} {'avg OAS (bps)':>16}"
        )
        for row in output_rows:
            print(
                f"{row['portfolio_or_benchmark']:<25} {row['valuation_date']:<12} "
                f"{Decimal(row['dirty_bond_market_value_usd']):>22,.2f} "
                f"{Decimal(row['cash_usd']):>16,.2f} "
                f"{Decimal(row['nav_usd']):>18,.2f} "
                f"{Decimal(row['cash_weight_decimal']) * 100:>13.6f}% "
                f"{Decimal(row['effective_duration_years']):>18.9f} "
                f"{Decimal(row['average_bond_oas_bps']):>16.6f}"
            )
        print()
        print(
            "Beginning benchmark checks passed: duration equals simple average "
            f"{simple_average_duration} years; OAS equals simple average "
            f"{simple_average_oas} bps."
        )
        print("Bond NAV weights plus cash weight equal 1 for every portfolio/date.")
        print(f"Saved simulated risk exposures to {output_path}")


if __name__ == "__main__":
    main()
