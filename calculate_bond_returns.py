"""Calculate simulated per-bond returns for March-April 2026.

30/360 US is an explicit project convention; the reviewed contract
excerpts specify a 360-day year of twelve 30-day months but do not
distinguish US from European 30/360.

Assumptions, not verified facts: no principal changes or extra interest
during the period. Valuations are end-of-day after coupon payments, and
coupon cash is retained without reinvestment.
"""

import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path


START_DATE = date(2026, 3, 31)
END_DATE = date(2026, 4, 30)
REQUIRED_DATES = {START_DATE, END_DATE}
BASE_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class BondReturn:
    beginning_ai: Decimal
    ending_ai: Decimal
    coupon_dates: tuple[date, ...]
    coupon_cash: Decimal
    beginning_dirty: Decimal
    ending_dirty: Decimal
    price_return: Decimal
    income_return: Decimal
    total_return: Decimal


def read_candidates(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        required = {
            "internal_id",
            "coupon_rate_decimal",
            "coupon_month_day_1",
            "coupon_month_day_2",
            "first_coupon_date",
            "maturity_date",
        }
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(f"{path.name} is missing required columns: {sorted(required)}")

        candidates: dict[str, dict[str, str]] = {}
        for line_number, row in enumerate(reader, start=2):
            internal_id = (row.get("internal_id") or "").strip()
            if not internal_id:
                raise ValueError(f"{path.name} row {line_number}: internal_id is empty")
            if internal_id in candidates:
                raise ValueError(f"{path.name} row {line_number}: duplicate internal_id {internal_id}")
            candidates[internal_id] = row

    if not candidates:
        raise ValueError(f"{path.name} contains no candidate bonds")
    return candidates


def read_prices(path: Path, candidate_ids: set[str]) -> dict[tuple[str, date], Decimal]:
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        required = {"internal_id", "valuation_date", "clean_price"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(f"{path.name} is missing required columns: {sorted(required)}")

        prices: dict[tuple[str, date], Decimal] = {}
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
            try:
                clean_price = Decimal(row["clean_price"])
            except (InvalidOperation, TypeError) as error:
                raise ValueError(
                    f"{path.name} row {line_number}: clean_price is not numeric: "
                    f"{row.get('clean_price')!r}"
                ) from error
            if not clean_price.is_finite() or clean_price <= 0:
                raise ValueError(
                    f"{path.name} row {line_number}: clean_price must be finite "
                    f"and positive, got {clean_price}"
                )

            key = (internal_id, valuation_date)
            if key in prices:
                raise ValueError(
                    f"{path.name} row {line_number}: duplicate bond/date pair "
                    f"{internal_id} {valuation_date.isoformat()}"
                )
            prices[key] = clean_price

    expected = {
        (internal_id, valuation_date)
        for internal_id in candidate_ids
        for valuation_date in REQUIRED_DATES
    }
    missing = expected - prices.keys()
    unexpected_dates = {
        key for key in prices if key[1] not in REQUIRED_DATES
    }
    if missing:
        details = ", ".join(
            f"{internal_id}@{valuation_date.isoformat()}"
            for internal_id, valuation_date in sorted(missing)
        )
        raise ValueError(f"{path.name} is missing required bond/date prices: {details}")
    if unexpected_dates:
        details = ", ".join(
            f"{internal_id}@{valuation_date.isoformat()}"
            for internal_id, valuation_date in sorted(unexpected_dates)
        )
        raise ValueError(f"{path.name} has unexpected valuation dates: {details}")
    return prices


def scheduled_coupon_dates(
    candidate: dict[str, str], first_coupon: date, maturity: date, start: date, end: date
) -> list[date]:
    dates: list[date] = []
    coupon_month_days = (
        candidate["coupon_month_day_1"],
        candidate["coupon_month_day_2"],
    )
    for year in range(start.year, end.year + 1):
        for month_day in coupon_month_days:
            month_text, day_text = month_day.split("-", maxsplit=1)
            coupon_date = date(year, int(month_text), int(day_text))
            if first_coupon <= coupon_date <= maturity and start < coupon_date <= end:
                dates.append(coupon_date)
    return sorted(dates)


def previous_coupon_date(candidate: dict[str, str], valuation_date: date) -> date:
    first_coupon = date.fromisoformat(candidate["first_coupon_date"])
    maturity = date.fromisoformat(candidate["maturity_date"])
    coupon_dates = []
    for year in range(first_coupon.year, valuation_date.year + 1):
        for month_day in (
            candidate["coupon_month_day_1"],
            candidate["coupon_month_day_2"],
        ):
            month_text, day_text = month_day.split("-", maxsplit=1)
            coupon_date = date(year, int(month_text), int(day_text))
            if first_coupon <= coupon_date <= maturity and coupon_date <= valuation_date:
                coupon_dates.append(coupon_date)
    if not coupon_dates:
        raise ValueError(
            f"No scheduled coupon on or before {valuation_date} for "
            f"{candidate['internal_id']}"
        )
    return max(coupon_dates)


def days_30_360_us(start: date, end: date) -> int:
    """Return 30/360 US days using the standard 31st-day adjustments."""
    day_1 = 30 if start.day == 31 else start.day
    day_2 = end.day
    if day_2 == 31 and day_1 == 30:
        day_2 = 30
    return (
        360 * (end.year - start.year)
        + 30 * (end.month - start.month)
        + day_2
        - day_1
    )


def accrued_interest(candidate: dict[str, str], valuation_date: date) -> Decimal:
    previous_coupon = previous_coupon_date(candidate, valuation_date)
    days = days_30_360_us(previous_coupon, valuation_date)
    annual_coupon_per_100 = Decimal(candidate["coupon_rate_decimal"]) * Decimal(100)
    return annual_coupon_per_100 * Decimal(days) / Decimal(360)


def calculate_bond_returns(
    candidates: dict[str, dict[str, str]],
    prices: dict[tuple[str, date], Decimal],
) -> dict[str, BondReturn]:
    """Calculate full-precision per-bond dirty values, income, and returns."""
    results: dict[str, BondReturn] = {}
    with localcontext() as context:
        context.prec = 50
        for internal_id, candidate in candidates.items():
            beginning_clean = prices[(internal_id, START_DATE)]
            ending_clean = prices[(internal_id, END_DATE)]
            beginning_ai = accrued_interest(candidate, START_DATE)
            ending_ai = accrued_interest(candidate, END_DATE)

            first_coupon = date.fromisoformat(candidate["first_coupon_date"])
            maturity = date.fromisoformat(candidate["maturity_date"])
            coupon_dates = tuple(
                scheduled_coupon_dates(
                    candidate, first_coupon, maturity, START_DATE, END_DATE
                )
            )
            semiannual_coupon = (
                Decimal(candidate["coupon_rate_decimal"]) * Decimal(100) / Decimal(2)
            )
            coupon_cash = semiannual_coupon * len(coupon_dates)

            beginning_dirty = beginning_clean + beginning_ai
            ending_dirty = ending_clean + ending_ai
            price_return = (ending_clean - beginning_clean) / beginning_dirty
            income_return = (coupon_cash + ending_ai - beginning_ai) / beginning_dirty
            results[internal_id] = BondReturn(
                beginning_ai=beginning_ai,
                ending_ai=ending_ai,
                coupon_dates=coupon_dates,
                coupon_cash=coupon_cash,
                beginning_dirty=beginning_dirty,
                ending_dirty=ending_dirty,
                price_return=price_return,
                income_return=income_return,
                total_return=price_return + income_return,
            )
    return results


def main() -> None:
    candidates = read_candidates(BASE_DIR / "bond_candidates.csv")
    prices = read_prices(BASE_DIR / "simulated_prices.csv", set(candidates))
    results = calculate_bond_returns(candidates, prices)

    print("Project convention: 30/360 US (not distinguished in reviewed excerpts).")
    print(
        "Simulation assumptions, not verified facts: no principal changes or extra "
        "interest; end-of-day valuations after coupon payments; coupon cash retained "
        "without reinvestment."
    )
    print("Returns are shown as percentages; prices and accrued interest are per $100 face.")
    print()
    print(
        f"{'internal_id':<27} {'begin AI':>14} {'end AI':>14} "
        f"{'coupon cash':>12} {'begin dirty':>14} {'end dirty':>14} "
        f"{'price rtn':>12} {'income rtn':>12} {'total rtn':>12}"
    )

    for internal_id, result in results.items():
        print(
            f"{internal_id:<27} {result.beginning_ai:>14.9f} {result.ending_ai:>14.9f} "
            f"{result.coupon_cash:>12.6f} {result.beginning_dirty:>14.9f} "
            f"{result.ending_dirty:>14.9f} {result.price_return * 100:>11.6f}% "
            f"{result.income_return * 100:>11.6f}% {result.total_return * 100:>11.6f}%"
        )

    print()
    print("Scheduled coupon payments in (2026-03-31, 2026-04-30]:")
    for internal_id, result in results.items():
        if result.coupon_dates:
            print(
                f"  {internal_id}: "
                + ", ".join(coupon_date.isoformat() for coupon_date in result.coupon_dates)
            )
    celanese = results["CELANESE_6.500_2030"]
    expected = (
        Decimal("2.997222222222222222222222222"),
        Decimal("0.2708333333333333333333333333"),
        Decimal("3.25"),
    )
    if any(
        abs(actual - target) > Decimal("1e-24")
        for actual, target in zip(
            (celanese.beginning_ai, celanese.ending_ai, celanese.coupon_cash),
            expected,
        )
    ):
        raise AssertionError(
            "Celanese accrued interest/coupon check failed: "
            f"{celanese.beginning_ai}, {celanese.ending_ai}, {celanese.coupon_cash}"
        )
    if abs(celanese.total_return * 100 - Decimal("1.5086")) > Decimal("0.0001"):
        raise AssertionError(f"Celanese total-return check failed: {celanese.total_return * 100}%")
    print()
    print(
        "Celanese worked-example check passed: beginning AI 2.997222..., "
        "ending AI 0.270833..., coupon cash 3.25, total return approximately 1.5086%."
    )


if __name__ == "__main__":
    main()
