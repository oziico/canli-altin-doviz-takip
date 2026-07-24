from datetime import timedelta

import pandas as pd


def calculate_24h_analysis(
    df_all: pd.DataFrame,
    latest: dict,
    metrics: list[str],
) -> tuple[dict, dict]:

    changes_24h = {}
    volatility_24h = {}

    last_time = pd.to_datetime(latest["timestamp"])
    threshold = last_time - timedelta(days=1)

    df_24h = (
        df_all[df_all["timestamp"] >= threshold]
        .sort_values("timestamp")
    )

    for metric in metrics:
        current_value = latest[metric]

        if not df_24h.empty and len(df_24h) >= 2:
            previous_value = df_24h[metric].iloc[0]

            percentage_change = (
                ((current_value - previous_value) / previous_value) * 100
                if previous_value > 0
                else 0.0
            )

            percentage_returns = (
                df_24h[metric]
                .pct_change()
                .dropna()
            )

            volatility = percentage_returns.std() * 100

        else:
            previous_value = current_value
            percentage_change = 0.0
            volatility = 0.0

        changes_24h[metric] = {
            "diff": current_value - previous_value,
            "pct": percentage_change,
        }

        volatility_24h[metric] = volatility

    return changes_24h, volatility_24h


def get_market_leaders(
    changes_24h: dict,
    volatility_24h: dict,
) -> tuple:

    sorted_changes = sorted(
        changes_24h.items(),
        key=lambda item: item[1]["pct"],
    )

    max_dropped = sorted_changes[0]
    max_gained = sorted_changes[-1]

    max_volatile_key = max(
        volatility_24h,
        key=volatility_24h.get,
    )

    max_volatility_value = volatility_24h[
        max_volatile_key
    ]

    return (
        max_dropped,
        max_gained,
        max_volatile_key,
        max_volatility_value,
    )

def add_time_based_moving_averages(
    df: pd.DataFrame,
    column: str,
    short_minutes: int = 30,
    long_minutes: int = 60,
) -> pd.DataFrame:
    """
    Zaman bazlı hareketli ortalamaları hesaplar.
    """

    result = df.copy()
    result = result.sort_values("timestamp")

    result = result.set_index("timestamp")

    result[f"{column}_ma_short"] = (
        result[column]
        .rolling(f"{short_minutes}min")
        .mean()
    )

    result[f"{column}_ma_long"] = (
        result[column]
        .rolling(f"{long_minutes}min")
        .mean()
    )

    return result.reset_index()


def calculate_time_based_trend(
    df: pd.DataFrame,
    column: str,
    short_minutes: int = 30,
    long_minutes: int = 60,
) -> str:
    """
    Kısa ve uzun dönem zaman bazlı hareketli ortalamaları
    karşılaştırarak trend yönünü belirler.

    Trend hesaplanabilmesi için yeterli zaman aralığında
    veri bulunması gerekir.
    """

    if df.empty or len(df) < 2:
        return "Yetersiz Veri"

    working_df = df.copy()

    working_df["timestamp"] = pd.to_datetime(
        working_df["timestamp"]
    )

    working_df = working_df.sort_values("timestamp")

    first_time = working_df["timestamp"].iloc[0]
    last_time = working_df["timestamp"].iloc[-1]

    available_minutes = (
        last_time - first_time
    ).total_seconds() / 60

    # Uzun dönem analizi için yeterli geçmiş yoksa
    # trend sonucu üretme.
    if available_minutes < long_minutes:
        return "Yetersiz Veri"

    analyzed_df = add_time_based_moving_averages(
        working_df,
        column,
        short_minutes,
        long_minutes,
    )

    short_ma = analyzed_df[
        f"{column}_ma_short"
    ].iloc[-1]

    long_ma = analyzed_df[
        f"{column}_ma_long"
    ].iloc[-1]

    if pd.isna(short_ma) or pd.isna(long_ma):
        return "Yetersiz Veri"

    if long_ma == 0:
        return "Yatay Seyir"

    difference_pct = (
        (short_ma - long_ma)
        / long_ma
    ) * 100

    if difference_pct > 0.05:
        return "Yükseliş Eğilimi"

    if difference_pct < -0.05:
        return "Düşüş Eğilimi"

    return "Yatay Seyir"