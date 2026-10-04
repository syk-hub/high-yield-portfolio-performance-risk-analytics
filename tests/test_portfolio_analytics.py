import math

from portfolio_analytics import calculate_bond_cash_flow, calculate_bond_return_metrics


def test_calculate_bond_cash_flow_matches_formula():
    cash = calculate_bond_cash_flow(
        face_amount=1000000,
        coupon_rate=0.065,
        frequency=2,
        settlement_date="2026-03-31",
        payment_date="2026-04-30",
        day_count="30/360",
    )

    assert math.isclose(cash, 32500.0, rel_tol=1e-9)


def test_calculate_bond_return_metrics_tracks_total_return_breakdown():
    metrics = calculate_bond_return_metrics(
        face_amount=1000000,
        begin_clean=98.5,
        end_clean=99.2,
        begin_accrued=1.25,
        end_accrued=0.9,
        coupon_cash=32500,
        begin_dirty_value=997500,
    )

    assert math.isclose(metrics["price_return"], 0.007017543859649151, rel_tol=1e-12)
    assert math.isclose(metrics["income_return"], 0.029072681704260653, rel_tol=1e-12)
    assert math.isclose(metrics["total_return"], 0.036090225563909895, rel_tol=1e-12)
    assert math.isclose(metrics["total_return"], metrics["price_return"] + metrics["income_return"], rel_tol=1e-12)
