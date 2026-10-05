"""Calculate illustrative portfolio returns from simulated bond returns."""

import csv
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path

from calculate_bond_returns import (
    BASE_DIR,
    INPUT_DIR,
    calculate_bond_returns,
    read_candidates,
    read_prices,
)


TOLERANCE = Decimal("1e-25")
BENCHMARK_WEIGHT = Decimal("0.10")


def decimal_text(value: Decimal) -> str:
    return format(value, "f")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_holdings(path: Path, candidate_ids: set[str]) -> dict[str, Decimal]:
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        required = {"internal_id", "face_value_usd"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(f"{path.name} is missing required columns: {sorted(required)}")

        holdings: dict[str, Decimal] = {}
        for line_number, row in enumerate(reader, start=2):
            internal_id = (row.get("internal_id") or "").strip()
            if not internal_id:
                raise ValueError(f"{path.name} row {line_number}: internal_id is empty")
            if internal_id in holdings:
                raise ValueError(
                    f"{path.name} row {line_number}: duplicate internal_id {internal_id}"
                )
            if internal_id not in candidate_ids:
                raise ValueError(
                    f"{path.name} row {line_number}: unknown internal_id {internal_id!r}"
                )
            try:
                face_value = Decimal(row["face_value_usd"])
            except (InvalidOperation, TypeError) as error:
                raise ValueError(
                    f"{path.name} row {line_number}: face_value_usd is not numeric: "
                    f"{row.get('face_value_usd')!r}"
                ) from error
            if not face_value.is_finite() or face_value <= 0:
                raise ValueError(
                    f"{path.name} row {line_number}: face_value_usd must be finite "
                    f"and positive, got {face_value}"
                )
            holdings[internal_id] = face_value

    missing = candidate_ids - holdings.keys()
    if missing:
        raise ValueError(
            f"{path.name} does not cover all candidates: {', '.join(sorted(missing))}"
        )
    if holdings.keys() != candidate_ids:
        raise ValueError(f"{path.name} must cover exactly the candidate IDs")
    return holdings


def main() -> None:
    with localcontext() as context:
        context.prec = 50
        candidates = read_candidates(INPUT_DIR / "bond_candidates.csv")
        prices = read_prices(INPUT_DIR / "simulated_prices.csv", set(candidates))
        holdings = read_holdings(INPUT_DIR / "portfolio_holdings.csv", set(candidates))
        bond_returns = calculate_bond_returns(candidates, prices)
        if len(bond_returns) != 10:
            raise ValueError(
                "The constructed same-universe benchmark requires exactly ten bonds"
            )

        beginning_values = {
            internal_id: holdings[internal_id] / Decimal(100) * result.beginning_dirty
            for internal_id, result in bond_returns.items()
        }
        beginning_nav = sum(beginning_values.values(), Decimal(0))
        if beginning_nav <= 0:
            raise ValueError("Beginning NAV must be positive")

        rows = []
        for internal_id, result in bond_returns.items():
            face_value = holdings[internal_id]
            beginning_market_value = beginning_values[internal_id]
            ending_market_value = face_value / Decimal(100) * result.ending_dirty
            coupon_cash_usd = face_value / Decimal(100) * result.coupon_cash
            beginning_weight = beginning_market_value / beginning_nav
            price_contribution = beginning_weight * result.price_return
            income_contribution = beginning_weight * result.income_return
            total_contribution = price_contribution + income_contribution
            active_weight = beginning_weight - BENCHMARK_WEIGHT
            active_contribution = active_weight * result.total_return
            rows.append(
                {
                    "internal_id": internal_id,
                    "face_value": face_value,
                    "beginning_market_value": beginning_market_value,
                    "ending_market_value": ending_market_value,
                    "coupon_cash": coupon_cash_usd,
                    "beginning_weight": beginning_weight,
                    "price_contribution": price_contribution,
                    "income_contribution": income_contribution,
                    "total_contribution": total_contribution,
                    "active_weight": active_weight,
                    "active_contribution": active_contribution,
                }
            )

        ending_dirty_market_value = sum(
            (row["ending_market_value"] for row in rows), Decimal(0)
        )
        total_coupon_cash = sum((row["coupon_cash"] for row in rows), Decimal(0))
        ending_nav = ending_dirty_market_value + total_coupon_cash
        portfolio_return = ending_nav / beginning_nav - Decimal(1)
        weights_sum = sum((row["beginning_weight"] for row in rows), Decimal(0))
        price_contributions = sum(
            (row["price_contribution"] for row in rows), Decimal(0)
        )
        income_contributions = sum(
            (row["income_contribution"] for row in rows), Decimal(0)
        )
        total_contributions = sum(
            (row["total_contribution"] for row in rows), Decimal(0)
        )
        benchmark_return = sum(
            (
                BENCHMARK_WEIGHT * result.total_return
                for result in bond_returns.values()
            ),
            Decimal(0),
        )
        active_return = portfolio_return - benchmark_return
        active_weights_sum = sum(
            (row["active_weight"] for row in rows), Decimal(0)
        )
        active_contributions = sum(
            (row["active_contribution"] for row in rows), Decimal(0)
        )

        if abs(weights_sum - Decimal(1)) > TOLERANCE:
            raise AssertionError(f"Beginning weights sum to {weights_sum}, not 1")
        if abs(total_contributions - portfolio_return) > TOLERANCE:
            raise AssertionError(
                "Weighted contributions do not reconcile to portfolio return: "
                f"{total_contributions} vs {portfolio_return}"
            )
        if abs(price_contributions + income_contributions - total_contributions) > TOLERANCE:
            raise AssertionError("Price and income contributions do not sum to total contributions")
        if abs(active_weights_sum) > TOLERANCE:
            raise AssertionError(f"Active weights sum to {active_weights_sum}, not 0")
        if abs(active_contributions - active_return) > TOLERANCE:
            raise AssertionError(
                "Active contributions do not reconcile to active return: "
                f"{active_contributions} vs {active_return}"
            )

        output_dir = BASE_DIR / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)

        bond_return_records = [
            {
                "internal_id": internal_id,
                "beginning_ai_usd_per_100_face": decimal_text(result.beginning_ai),
                "ending_ai_usd_per_100_face": decimal_text(result.ending_ai),
                "coupon_cash_usd_per_100_face": decimal_text(result.coupon_cash),
                "beginning_dirty_price_usd_per_100_face": decimal_text(
                    result.beginning_dirty
                ),
                "ending_dirty_price_usd_per_100_face": decimal_text(result.ending_dirty),
                "price_return_decimal": decimal_text(result.price_return),
                "income_return_decimal": decimal_text(result.income_return),
                "total_return_decimal": decimal_text(result.total_return),
                "coupon_payment_dates": ";".join(
                    coupon_date.isoformat() for coupon_date in result.coupon_dates
                ),
                "result_status": "simulated",
            }
            for internal_id, result in bond_returns.items()
        ]
        write_csv(
            output_dir / "bond_returns.csv",
            [
                "internal_id",
                "beginning_ai_usd_per_100_face",
                "ending_ai_usd_per_100_face",
                "coupon_cash_usd_per_100_face",
                "beginning_dirty_price_usd_per_100_face",
                "ending_dirty_price_usd_per_100_face",
                "price_return_decimal",
                "income_return_decimal",
                "total_return_decimal",
                "coupon_payment_dates",
                "result_status",
            ],
            bond_return_records,
        )

        contribution_records = [
            {
                "internal_id": row["internal_id"],
                "face_value_usd": decimal_text(row["face_value"]),
                "beginning_dirty_market_value_usd": decimal_text(
                    row["beginning_market_value"]
                ),
                "ending_dirty_market_value_usd": decimal_text(
                    row["ending_market_value"]
                ),
                "coupon_cash_usd": decimal_text(row["coupon_cash"]),
                "beginning_weight_decimal": decimal_text(row["beginning_weight"]),
                "price_contribution_decimal": decimal_text(row["price_contribution"]),
                "income_contribution_decimal": decimal_text(row["income_contribution"]),
                "total_contribution_decimal": decimal_text(row["total_contribution"]),
                "result_status": "simulated",
            }
            for row in rows
        ]
        write_csv(
            output_dir / "portfolio_contributions.csv",
            [
                "internal_id",
                "face_value_usd",
                "beginning_dirty_market_value_usd",
                "ending_dirty_market_value_usd",
                "coupon_cash_usd",
                "beginning_weight_decimal",
                "price_contribution_decimal",
                "income_contribution_decimal",
                "total_contribution_decimal",
                "result_status",
            ],
            contribution_records,
        )

        active_contribution_records = [
            {
                "internal_id": row["internal_id"],
                "portfolio_beginning_weight_decimal": decimal_text(
                    row["beginning_weight"]
                ),
                "benchmark_beginning_weight_decimal": decimal_text(BENCHMARK_WEIGHT),
                "active_weight_decimal": decimal_text(row["active_weight"]),
                "bond_total_return_decimal": decimal_text(
                    bond_returns[row["internal_id"]].total_return
                ),
                "active_contribution_decimal": decimal_text(
                    row["active_contribution"]
                ),
                "result_status": "simulated",
            }
            for row in rows
        ]
        write_csv(
            output_dir / "active_contributions.csv",
            [
                "internal_id",
                "portfolio_beginning_weight_decimal",
                "benchmark_beginning_weight_decimal",
                "active_weight_decimal",
                "bond_total_return_decimal",
                "active_contribution_decimal",
                "result_status",
            ],
            active_contribution_records,
        )

        summary_records = [
            {
                "metric": "beginning_nav",
                "value": decimal_text(beginning_nav),
                "unit": "USD",
                "result_status": "simulated",
            },
            {
                "metric": "ending_dirty_bond_value",
                "value": decimal_text(ending_dirty_market_value),
                "unit": "USD",
                "result_status": "simulated",
            },
            {
                "metric": "coupon_cash",
                "value": decimal_text(total_coupon_cash),
                "unit": "USD",
                "result_status": "simulated",
            },
            {
                "metric": "ending_nav",
                "value": decimal_text(ending_nav),
                "unit": "USD",
                "result_status": "simulated",
            },
            {
                "metric": "portfolio_return",
                "value": decimal_text(portfolio_return),
                "unit": "decimal_return",
                "result_status": "simulated",
            },
            {
                "metric": "benchmark_return",
                "value": decimal_text(benchmark_return),
                "unit": "decimal_return",
                "result_status": "simulated",
            },
            {
                "metric": "active_return",
                "value": decimal_text(active_return),
                "unit": "decimal_return",
                "result_status": "simulated",
            },
        ]
        write_csv(
            output_dir / "performance_summary.csv",
            ["metric", "value", "unit", "result_status"],
            summary_records,
        )
        (output_dir / "README.md").write_text(
            "# Simulated outputs\n\n"
            "These CSVs contain simulated teaching results derived from simulated "
            "bond prices and teaching allocations. Returns and weights are stored "
            "as decimals at full calculation precision; monetary values are in USD "
            "unless the column name specifies USD per $100 face. The benchmark is "
            "a constructed same-universe benchmark, not a market index.\n",
            encoding="utf-8",
        )

        print(
            "Assumptions: zero beginning cash, unchanged face amounts, coupon cash "
            "retained at zero interest."
        )
        print(
            "Benchmark: constructed same-universe benchmark, 10% beginning "
            "dirty-market-value weight in each bond; positions held fixed during "
            "April and coupon cash retained at zero interest. Not a market index."
        )
        print("Amounts are USD; contributions and weights are percentages.")
        print()
        print(
            f"{'internal_id':<27} {'face value':>14} {'begin MV':>16} "
            f"{'end dirty MV':>16} {'coupon cash':>14} {'begin weight':>14} "
            f"{'price contrib':>15} {'income contrib':>16} {'total contrib':>15} "
            f"{'active weight':>14} {'active contrib':>15}"
        )
        for row in rows:
            print(
                f"{row['internal_id']:<27} {row['face_value']:>14,.2f} "
                f"{row['beginning_market_value']:>16,.2f} "
                f"{row['ending_market_value']:>16,.2f} {row['coupon_cash']:>14,.2f} "
                f"{row['beginning_weight'] * 100:>13.6f}% "
                f"{row['price_contribution'] * 100:>14.6f} pp "
                f"{row['income_contribution'] * 100:>15.6f} pp "
                f"{row['total_contribution'] * 100:>14.6f} pp "
                f"{row['active_weight'] * 100:>13.6f}% "
                f"{row['active_contribution'] * 100:>14.6f} pp"
            )

        print()
        print(f"Beginning NAV (zero beginning cash): ${beginning_nav:,.2f}")
        print(f"Ending dirty market value:            ${ending_dirty_market_value:,.2f}")
        print(f"Ending coupon cash (zero interest):   ${total_coupon_cash:,.2f}")
        print(f"Ending NAV:                           ${ending_nav:,.2f}")
        print(f"Beginning weights sum:                {weights_sum * 100:.12f}%")
        print(f"Price contributions:                  {price_contributions * 100:.6f} pp")
        print(f"Income contributions:                 {income_contributions * 100:.6f} pp")
        print(f"Total contributions:                  {total_contributions * 100:.6f} pp")
        print(f"Active weights sum:                   {active_weights_sum * 100:.12f}%")
        print(f"Active contributions:                 {active_contributions * 100:.6f} pp")
        print(f"Constructed benchmark return:         {benchmark_return * 100:.6f}%")
        print(f"Portfolio return:                     {portfolio_return * 100:.6f}%")
        print(f"Active return (portfolio - benchmark): {active_return * 100:.6f}%")
        print("NAV, contribution, active-weight, and active-return reconciliations passed.")


if __name__ == "__main__":
    main()
