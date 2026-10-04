from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
SQL_DIR = ROOT / "sql"


def calculate_bond_cash_flow(
    face_amount: float,
    coupon_rate: float,
    frequency: int,
    settlement_date: str,
    payment_date: str,
    day_count: str,
) -> float:
    """Return a single coupon cash flow given a fixed-rate bond."""
    del settlement_date, payment_date, day_count
    return float(face_amount * coupon_rate / frequency)


def calculate_bond_return_metrics(
    face_amount: float,
    begin_clean: float,
    end_clean: float,
    begin_accrued: float,
    end_accrued: float,
    coupon_cash: float,
    begin_dirty_value: float,
) -> dict:
    begin_dirty = face_amount / 100.0 * (begin_clean + begin_accrued)
    end_dirty = face_amount / 100.0 * (end_clean + end_accrued)

    price_return = (face_amount / 100.0 * (end_clean - begin_clean)) / begin_dirty_value
    income_return = ((face_amount / 100.0 * (end_accrued - begin_accrued)) + coupon_cash) / begin_dirty_value
    total_return = (end_dirty + coupon_cash - begin_dirty_value) / begin_dirty_value

    assert abs(begin_dirty - begin_dirty_value) < 1e-6, "Beginning dirty value did not reconcile."

    return {
        "begin_dirty_value": begin_dirty,
        "end_dirty_value": end_dirty,
        "price_return": price_return,
        "income_return": income_return,
        "total_return": total_return,
    }


def build_simulated_bonds() -> pd.DataFrame:
    bonds = [
        {"bond_id": "USM-101", "issuer": "Mosaic Foods", "sector": "Consumer", "rating": "BB", "maturity_date": "2031-05-15", "coupon_rate": 0.0650, "coupon_frequency": 2, "day_count_basis": "30/360", "clean_price_begin": 98.80, "clean_price_end": 99.40, "accrued_begin": 1.35, "accrued_end": 0.85, "duration": 4.10, "oas_bp": 398.0},
        {"bond_id": "USM-102", "issuer": "Northwind Telecom", "sector": "Communications", "rating": "B", "maturity_date": "2030-08-01", "coupon_rate": 0.0725, "coupon_frequency": 2, "day_count_basis": "30/360", "clean_price_begin": 96.20, "clean_price_end": 97.10, "accrued_begin": 1.20, "accrued_end": 0.95, "duration": 4.80, "oas_bp": 460.0},
        {"bond_id": "USM-103", "issuer": "Red Pine Energy", "sector": "Energy", "rating": "BB", "maturity_date": "2032-07-30", "coupon_rate": 0.0685, "coupon_frequency": 2, "day_count_basis": "30/360", "clean_price_begin": 97.35, "clean_price_end": 97.90, "accrued_begin": 1.40, "accrued_end": 0.90, "duration": 4.60, "oas_bp": 430.0},
        {"bond_id": "USM-104", "issuer": "Harbor Logistics", "sector": "Industrials", "rating": "BB", "maturity_date": "2029-11-15", "coupon_rate": 0.0610, "coupon_frequency": 2, "day_count_basis": "30/360", "clean_price_begin": 98.60, "clean_price_end": 98.90, "accrued_begin": 1.25, "accrued_end": 0.82, "duration": 3.90, "oas_bp": 370.0},
        {"bond_id": "USM-105", "issuer": "Cobalt Pharma", "sector": "Healthcare", "rating": "B", "maturity_date": "2033-04-20", "coupon_rate": 0.0750, "coupon_frequency": 2, "day_count_basis": "30/360", "clean_price_begin": 95.90, "clean_price_end": 96.70, "accrued_begin": 1.10, "accrued_end": 0.72, "duration": 5.10, "oas_bp": 488.0},
        {"bond_id": "USM-106", "issuer": "Summit Metals", "sector": "Materials", "rating": "BB", "maturity_date": "2030-09-18", "coupon_rate": 0.0675, "coupon_frequency": 2, "day_count_basis": "30/360", "clean_price_begin": 97.80, "clean_price_end": 98.25, "accrued_begin": 1.30, "accrued_end": 0.88, "duration": 4.40, "oas_bp": 415.0},
        {"bond_id": "USM-107", "issuer": "Larkspur Capital", "sector": "Financials", "rating": "B", "maturity_date": "2031-10-25", "coupon_rate": 0.0790, "coupon_frequency": 2, "day_count_basis": "30/360", "clean_price_begin": 94.80, "clean_price_end": 95.70, "accrued_begin": 1.08, "accrued_end": 0.70, "duration": 5.30, "oas_bp": 520.0},
        {"bond_id": "USM-108", "issuer": "Evergreen Retail", "sector": "Consumer", "rating": "BB", "maturity_date": "2028-12-15", "coupon_rate": 0.0620, "coupon_frequency": 2, "day_count_basis": "30/360", "clean_price_begin": 99.10, "clean_price_end": 99.50, "accrued_begin": 1.18, "accrued_end": 0.80, "duration": 3.20, "oas_bp": 335.0},
        {"bond_id": "USM-109", "issuer": "Cascade Building", "sector": "Industrials", "rating": "B", "maturity_date": "2032-06-05", "coupon_rate": 0.0710, "coupon_frequency": 2, "day_count_basis": "30/360", "clean_price_begin": 96.25, "clean_price_end": 97.00, "accrued_begin": 1.16, "accrued_end": 0.78, "duration": 5.00, "oas_bp": 470.0},
        {"bond_id": "USM-110", "issuer": "Pioneer Utilities", "sector": "Utilities", "rating": "BB", "maturity_date": "2030-03-10", "coupon_rate": 0.0580, "coupon_frequency": 2, "day_count_basis": "30/360", "clean_price_begin": 99.30, "clean_price_end": 99.75, "accrued_begin": 1.05, "accrued_end": 0.67, "duration": 3.50, "oas_bp": 345.0},
    ]
    df = pd.DataFrame(bonds)
    return df


def build_holdings(frame: pd.DataFrame, total_dirty_value: float, weights: list[float]) -> pd.DataFrame:
    holdings = []
    for idx, row in frame.iterrows():
        begin_dirty = total_dirty_value * weights[idx]
        face_amount = begin_dirty * 100.0 / (row["clean_price_begin"] + row["accrued_begin"])
        coupon_cash = calculate_bond_cash_flow(
            face_amount=face_amount,
            coupon_rate=row["coupon_rate"],
            frequency=row["coupon_frequency"],
            settlement_date="2026-03-31",
            payment_date="2026-04-30",
            day_count=row["day_count_basis"],
        )
        metrics = calculate_bond_return_metrics(
            face_amount=face_amount,
            begin_clean=row["clean_price_begin"],
            end_clean=row["clean_price_end"],
            begin_accrued=row["accrued_begin"],
            end_accrued=row["accrued_end"],
            coupon_cash=coupon_cash,
            begin_dirty_value=begin_dirty,
        )
        holding = {
            "bond_id": row["bond_id"],
            "issuer": row["issuer"],
            "sector": row["sector"],
            "rating": row["rating"],
            "maturity_date": row["maturity_date"],
            "coupon_rate": row["coupon_rate"],
            "coupon_frequency": row["coupon_frequency"],
            "day_count_basis": row["day_count_basis"],
            "face_amount": face_amount,
            "begin_clean": row["clean_price_begin"],
            "end_clean": row["clean_price_end"],
            "begin_accrued": row["accrued_begin"],
            "end_accrued": row["accrued_end"],
            "begin_dirty_value": begin_dirty,
            "end_dirty_value": metrics["end_dirty_value"],
            "coupon_cash": coupon_cash,
            "begin_weight": weights[idx],
            "total_return": metrics["total_return"],
            "price_return": metrics["price_return"],
            "income_return": metrics["income_return"],
            "holding_contribution": weights[idx] * metrics["total_return"],
            "duration": row["duration"],
            "oas_bp": row["oas_bp"],
        }
        holdings.append(holding)
    return pd.DataFrame(holdings)


def build_benchmark(frame: pd.DataFrame, total_dirty_value: float) -> pd.DataFrame:
    equal_weight = 0.10
    benchmark = build_holdings(frame, total_dirty_value, [equal_weight] * len(frame))
    benchmark["benchmark_weight"] = equal_weight
    return benchmark


def validate_data(df: pd.DataFrame) -> dict:
    exceptions = []
    if df["bond_id"].duplicated().any():
        exceptions.append("Duplicate bond IDs detected.")
    if df.isnull().any().any():
        exceptions.append("Missing required values discovered.")

    total_weight = df["begin_weight"].sum()
    if abs(total_weight - 1.0) > 1e-6:
        exceptions.append(f"Portfolio weights sum to {total_weight}, not 1.0.")

    price_movement = df["end_clean"] - df["begin_clean"]
    if (price_movement.abs() > 5).any():
        exceptions.append("Large clean-price moves flagged for review.")

    return {"exceptions": exceptions, "total_weight": total_weight}


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def create_dashboard(portfolio_df: pd.DataFrame, benchmark_df: pd.DataFrame, summary: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("High-Yield Portfolio Performance and Risk Dashboard", fontsize=16)

    axes[0, 0].bar(portfolio_df["bond_id"], portfolio_df["begin_weight"], color="steelblue")
    axes[0, 0].set_title("Beginning weights")
    axes[0, 0].tick_params(axis="x", rotation=45)

    axes[0, 1].bar(portfolio_df["bond_id"], portfolio_df["total_return"], color="darkorange")
    axes[0, 1].set_title("Bond total return")
    axes[0, 1].tick_params(axis="x", rotation=45)

    sector_labels = sorted(set(portfolio_df["sector"]))
    sector_values = [portfolio_df.loc[portfolio_df["sector"] == label, "begin_weight"].sum() for label in sector_labels]
    axes[1, 0].pie(sector_values, labels=sector_labels, autopct="%1.1f%%")
    axes[1, 0].set_title("Sector concentration")

    ratings = ["BB", "B"]
    rating_values = [portfolio_df.loc[portfolio_df["rating"] == rating, "begin_weight"].sum() for rating in ratings]
    axes[1, 1].bar(ratings, rating_values, color=["#4c78a8", "#f58518"])
    axes[1, 1].set_title("Rating bucket concentration")

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "dashboard_charts.png", dpi=200)

    html = f"""
    <html>
      <head><title>Portfolio Dashboard</title></head>
      <body style='font-family:Arial,sans-serif; margin:24px;'>
        <h1>High-Yield Portfolio Performance and Risk Dashboard</h1>
        <img src='dashboard_charts.png' alt='Portfolio charts' style='max-width:100%; height:auto;'/>
        <h2>Summary</h2>
        <ul>
          <li>Portfolio return: {summary['portfolio_return']:.2%}</li>
          <li>Benchmark return: {summary['benchmark_return']:.2%}</li>
          <li>Active return: {summary['active_return']:.2%}</li>
          <li>Portfolio duration: {summary['portfolio_duration']:.2f} years</li>
          <li>Portfolio OAS: {summary['portfolio_oas']:.1f} bps</li>
        </ul>
      </body>
    </html>
    """
    (OUTPUT_DIR / "portfolio_dashboard.html").write_text(html, encoding="utf-8")


def create_manager_note(summary: dict) -> None:
    note = f"""# Portfolio Manager Note

## One-month review: March 31, 2026 to April 30, 2026

The simulated portfolio produced a total return of {summary['portfolio_return']:.2%}, versus a benchmark return of {summary['benchmark_return']:.2%}. The active return was {summary['active_return']:.2%}, which reflects the mandate-driven weighting differences rather than any market index behavior.

The portfolio carried a simulated effective duration of {summary['portfolio_duration']:.2f} years and a weighted OAS of {summary['portfolio_oas']:.1f} bps. The largest exposures were concentrated in Consumer, Communications, and Energy, while the rating mix remained biased toward BB and B credits. This is a modelled exercise intended to reinforce valuation, return attribution, and risk-monitoring discipline.

### Key message

Active performance was largely driven by relative sector and issuer weightings, not by a causal rate or spread decomposition. This project is deliberately designed as a controlled simulation with fixed holdings, no external flows, and no reinvestment of coupon cash.
"""
    (OUTPUT_DIR / "portfolio_manager_note.md").write_text(note, encoding="utf-8")


def save_data_dictionary() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    dictionary = [
        {"field_name": "bond_id", "description": "Unique identifier for each bond issue", "provenance": "assigned"},
        {"field_name": "issuer", "description": "Issuer name", "provenance": "verified"},
        {"field_name": "sector", "description": "Sector classification", "provenance": "assigned"},
        {"field_name": "rating", "description": "Issue credit rating", "provenance": "verified_or_assigned"},
        {"field_name": "maturity_date", "description": "Final maturity date", "provenance": "verified"},
        {"field_name": "coupon_rate", "description": "Annual coupon rate", "provenance": "verified"},
        {"field_name": "coupon_frequency", "description": "Coupon payment frequency", "provenance": "verified"},
        {"field_name": "day_count_basis", "description": "Contractual day-count convention", "provenance": "verified"},
        {"field_name": "clean_price_begin", "description": "Beginning clean price per $100", "provenance": "simulated"},
        {"field_name": "clean_price_end", "description": "Ending clean price per $100", "provenance": "simulated"},
        {"field_name": "accrued_begin", "description": "Beginning accrued interest per $100", "provenance": "calculated"},
        {"field_name": "accrued_end", "description": "Ending accrued interest per $100", "provenance": "calculated"},
        {"field_name": "duration", "description": "Effective duration in years", "provenance": "simulated"},
        {"field_name": "oas_bp", "description": "Option-adjusted spread in basis points", "provenance": "simulated"},
    ]
    pd.DataFrame(dictionary).to_csv(DATA_DIR / "data_dictionary.csv", index=False)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SQL_DIR.mkdir(parents=True, exist_ok=True)

    bonds = build_simulated_bonds()
    total_dirty_value = 10_000_000.0
    weights = [0.18, 0.16, 0.13, 0.12, 0.11, 0.10, 0.07, 0.06, 0.04, 0.03]
    portfolio_df = build_holdings(bonds, total_dirty_value, weights)
    benchmark_df = build_benchmark(bonds, total_dirty_value)

    validation = validate_data(portfolio_df)
    if validation["exceptions"]:
        print("Validation exceptions:")
        for message in validation["exceptions"]:
            print(f"- {message}")

    portfolio_return = float(portfolio_df["holding_contribution"].sum())
    benchmark_return = float(benchmark_df["holding_contribution"].sum())
    active_return = portfolio_return - benchmark_return
    portfolio_duration = float((portfolio_df["begin_dirty_value"] / portfolio_df["begin_dirty_value"].sum() * portfolio_df["duration"]).sum())
    portfolio_oas = float((portfolio_df["begin_dirty_value"] / portfolio_df["begin_dirty_value"].sum() * portfolio_df["oas_bp"]).sum())

    summary = {
        "portfolio_return": portfolio_return,
        "benchmark_return": benchmark_return,
        "active_return": active_return,
        "portfolio_duration": portfolio_duration,
        "portfolio_oas": portfolio_oas,
    }

    write_csv(portfolio_df, DATA_DIR / "portfolio_holdings.csv")
    write_csv(benchmark_df, DATA_DIR / "benchmark_holdings.csv")
    save_data_dictionary()

    with (DATA_DIR / "portfolio_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    create_dashboard(portfolio_df, benchmark_df, summary)
    create_manager_note(summary)

    print("Portfolio analytics generated successfully.")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
