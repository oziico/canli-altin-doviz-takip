import pandas as pd

from analytics import (
    TREND_DOWN,
    TREND_FLAT,
    TREND_NO_DATA,
    TREND_UP,
    calculate_percentage_change,
    calculate_time_based_trend,
)


def test_percentage_change_increase():
    assert calculate_percentage_change(110, 100) == 10.0


def test_percentage_change_decrease():
    assert calculate_percentage_change(90, 100) == -10.0


def test_percentage_change_zero_previous():
    assert calculate_percentage_change(100, 0) == 0.0


def test_trend_no_data():
    df = pd.DataFrame(
        {
            "timestamp": [],
            "usd_try": [],
        }
    )

    assert (
        calculate_time_based_trend(df, "usd_try")
        == TREND_NO_DATA
    )


def test_trend_up():
    timestamps = pd.date_range(
        "2026-01-01",
        periods=70,
        freq="min",
    )

    values = list(range(70))

    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "usd_try": values,
        }
    )

    assert (
        calculate_time_based_trend(df, "usd_try")
        == TREND_UP
    )


def test_trend_down():
    timestamps = pd.date_range(
        "2026-01-01",
        periods=70,
        freq="min",
    )

    values = list(range(70, 0, -1))

    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "usd_try": values,
        }
    )

    assert (
        calculate_time_based_trend(df, "usd_try")
        == TREND_DOWN
    )


def test_trend_flat():
    timestamps = pd.date_range(
        "2026-01-01",
        periods=70,
        freq="min",
    )

    values = [100] * 70

    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "usd_try": values,
        }
    )

    assert (
        calculate_time_based_trend(df, "usd_try")
        == TREND_FLAT
    )