from datetime import datetime
import logging
import requests

from config import (
    TWELVE_DATA_API_KEY,
    TWELVE_DATA_API_URL,
    GOLD_API_URL,
    REQUEST_TIMEOUT,
    OUNCE_TO_GRAM,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def get_forex_price(symbol: str) -> float | None:
    """
    Twelve Data üzerinden döviz çiftinin
    son 1 dakikalık kapanış fiyatını alır.
    """

    if not TWELVE_DATA_API_KEY:
        logger.error("TWELVE_DATA_API_KEY bulunamadı.")
        return None

    try:
        response = requests.get(
            f"{TWELVE_DATA_API_URL}/time_series",
            params={
                "symbol": symbol,
                "interval": "1min",
                "outputsize": 1,
                "apikey": TWELVE_DATA_API_KEY,
            },
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()
        data = response.json()

        if data.get("status") == "error":
            logger.error(
                f"Twelve Data API Hatası ({symbol}): "
                f"{data.get('message')}"
            )
            return None

        values = data.get("values")

        if not values:
            logger.error(
                f"{symbol} için zaman serisi bulunamadı."
            )
            return None

        latest_candle = values[0]

        close_price = latest_candle.get("close")

        if close_price is None:
            logger.error(
                f"{symbol} için kapanış fiyatı bulunamadı."
            )
            return None

        logger.info(
            f"{symbol} güncel fiyat: "
            f"{close_price} "
            f"({latest_candle.get('datetime')})"
        )

        return float(close_price)

    except requests.exceptions.RequestException as error:
        logger.error(
            f"Döviz API bağlantı hatası ({symbol}): {error}"
        )
        return None

    except (ValueError, TypeError) as error:
        logger.error(
            f"Döviz veri formatı hatası ({symbol}): {error}"
        )
        return None


def get_exchange_rates() -> dict | None:
    """
    USD/TRY, EUR/TRY ve GBP/TRY güncel fiyatlarını alır.
    """

    usd_try = get_forex_price("USD/TRY")
    eur_try = get_forex_price("EUR/TRY")
    gbp_try = get_forex_price("GBP/TRY")

    if (
        usd_try is None
        or eur_try is None
        or gbp_try is None
    ):
        logger.error(
            "Döviz verilerinin tamamı alınamadı."
        )
        return None

    logger.info(
        "Güncel döviz verileri başarıyla alındı."
    )

    return {
        "usd_try": round(usd_try, 4),
        "eur_try": round(eur_try, 4),
        "gbp_try": round(gbp_try, 4),
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    }


def calculate_gram_gold(
    ounce_price: float,
    usd_try: float,
) -> float:

    gram_gold = (
        ounce_price * usd_try
    ) / OUNCE_TO_GRAM

    return round(
        gram_gold,
        2,
    )


def get_gold_price() -> float | None:

    try:
        response = requests.get(
            GOLD_API_URL,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        gold_price = float(
            data["price"]
        )

        logger.info(
            "Ons altın fiyatı başarıyla alındı."
        )

        return gold_price

    except requests.exceptions.RequestException as error:

        logger.error(
            f"Altın API Hatası: {error}"
        )

        return None

    except (
        KeyError,
        ValueError,
        TypeError,
    ) as error:

        logger.error(
            f"Altın verisi işlenemedi: {error}"
        )

        return None


def get_market_data() -> dict | None:

    exchange_rates = get_exchange_rates()

    ounce_price = get_gold_price()

    if (
        exchange_rates is None
        or ounce_price is None
    ):
        return None

    market_data = {

        "usd_try":
            exchange_rates["usd_try"],

        "eur_try":
            exchange_rates["eur_try"],

        "gbp_try":
            exchange_rates["gbp_try"],

        "gold_ounce":
            round(
                ounce_price,
                2,
            ),

        "gold_gram":
            calculate_gram_gold(
                ounce_price,
                exchange_rates["usd_try"],
            ),

        "timestamp":
            exchange_rates["timestamp"],
    }

    logger.info(
        "Piyasa verileri başarıyla oluşturuldu."
    )

    return market_data


if __name__ == "__main__":

    market_data = get_market_data()

    if market_data:

        print("\n--- GÜNCEL PİYASA VERİLERİ ---")

        print(
            f"USD/TRY: "
            f"{market_data['usd_try']}"
        )

        print(
            f"EUR/TRY: "
            f"{market_data['eur_try']}"
        )

        print(
            f"GBP/TRY: "
            f"{market_data['gbp_try']}"
        )

        print(
            f"Ons Altın: "
            f"{market_data['gold_ounce']}"
        )

        print(
            f"Gram Altın: "
            f"{market_data['gold_gram']}"
        )

        print(
            f"Zaman: "
            f"{market_data['timestamp']}"
        )