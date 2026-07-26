from datetime import datetime
import logging

import requests

from config import (
    GOLD_API_URL,
    OUNCE_TO_GRAM,
    REQUEST_TIMEOUT,
    TWELVE_DATA_API_KEY,
    TWELVE_DATA_API_URL,
)


TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def current_timestamp() -> str:
    return datetime.now().strftime(TIMESTAMP_FORMAT)


def get_forex_price(symbol: str) -> float | None:
    """Twelve Data üzerinden döviz çiftinin son fiyatını döndürür."""

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
                "Twelve Data API hatası (%s): %s",
                symbol,
                data.get("message"),
            )
            return None

        values = data.get("values")
        if not values:
            logger.error("%s için zaman serisi bulunamadı.", symbol)
            return None

        latest = values[0]
        close_price = latest.get("close")

        if close_price is None:
            logger.error("%s için kapanış fiyatı bulunamadı.", symbol)
            return None

        logger.info(
            "%s güncel fiyat: %s (%s)",
            symbol,
            close_price,
            latest.get("datetime"),
        )

        return float(close_price)

    except requests.exceptions.RequestException as error:
        logger.error("Döviz API bağlantı hatası (%s): %s", symbol, error)
        return None

    except (ValueError, TypeError) as error:
        logger.error("Döviz veri formatı hatası (%s): %s", symbol, error)
        return None


def get_exchange_rates() -> dict | None:
    """USD/TRY, EUR/TRY ve GBP/TRY verilerini döndürür."""

    exchange_rates = {
        "usd_try": get_forex_price("USD/TRY"),
        "eur_try": get_forex_price("EUR/TRY"),
        "gbp_try": get_forex_price("GBP/TRY"),
    }

    if any(value is None for value in exchange_rates.values()):
        logger.error("Döviz verilerinin tamamı alınamadı.")
        return None

    exchange_rates = {
        key: round(value, 4)
        for key, value in exchange_rates.items()
    }
    exchange_rates["timestamp"] = current_timestamp()

    logger.info("Güncel döviz verileri başarıyla alındı.")

    return exchange_rates


def calculate_gram_gold(
    ounce_price: float,
    usd_try: float,
) -> float:
    """Gram altın fiyatını hesaplar."""
    return round((ounce_price * usd_try) / OUNCE_TO_GRAM, 2)


def get_gold_price() -> float | None:
    """Ons altın fiyatını döndürür."""
    try:
        response = requests.get(
            GOLD_API_URL,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()

        gold_price = float(response.json()["price"])

        logger.info("Ons altın fiyatı başarıyla alındı.")

        return gold_price

    except requests.exceptions.RequestException as error:
        logger.error("Altın API hatası: %s", error)
        return None

    except (KeyError, ValueError, TypeError) as error:
        logger.error("Altın verisi işlenemedi: %s", error)
        return None


def get_market_data() -> dict | None:
    """Tüm piyasa verilerini tek sözlükte toplar."""
    exchange_rates = get_exchange_rates()
    ounce_price = get_gold_price()

    if exchange_rates is None or ounce_price is None:
        return None

    market_data = {
        **exchange_rates,
        "gold_ounce": round(ounce_price, 2),
        "gold_gram": calculate_gram_gold(
            ounce_price,
            exchange_rates["usd_try"],
        ),
    }

    logger.info("Piyasa verileri başarıyla oluşturuldu.")

    return market_data


if __name__ == "__main__":
    market_data = get_market_data()

    if market_data:
        print("\n--- GÜNCEL PİYASA VERİLERİ ---")
        print(f"USD/TRY: {market_data['usd_try']}")
        print(f"EUR/TRY: {market_data['eur_try']}")
        print(f"GBP/TRY: {market_data['gbp_try']}")
        print(f"Ons Altın: {market_data['gold_ounce']}")
        print(f"Gram Altın: {market_data['gold_gram']}")
        print(f"Zaman: {market_data['timestamp']}")