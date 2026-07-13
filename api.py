"""
api.py Canlı altın ve döviz verilerini API'lerden çeker.
"""

from datetime import datetime
import logging

import requests

from config import (
    FRANKFURTER_API_URL,
    GOLD_API_URL,
    REQUEST_TIMEOUT,
    OUNCE_TO_GRAM,
)

# Logger ayarları
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def get_exchange_rates() -> dict | None:

    try:
        response = requests.get(
            FRANKFURTER_API_URL,
            params={
                "from": "USD",
                "to": "TRY,EUR,GBP",
            },
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        usd_try = data["rates"]["TRY"]

        response = requests.get(
            FRANKFURTER_API_URL,
            params={
                "from": "EUR",
                "to": "TRY",
            },
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        eur_try = response.json()["rates"]["TRY"]

        response = requests.get(
            FRANKFURTER_API_URL,
            params={
                "from": "GBP",
                "to": "TRY",
            },
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        gbp_try = response.json()["rates"]["TRY"]

        logger.info("Döviz verileri başarıyla alındı.")

        return {
            "usd_try": round(usd_try, 4),
            "eur_try": round(eur_try, 4),
            "gbp_try": round(gbp_try, 4),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    except requests.exceptions.RequestException as error:
        logger.error(f"Döviz API Hatası: {error}")
        return None


def calculate_gram_gold(ounce_price: float, usd_try: float) -> float:
    gram_gold = (ounce_price * usd_try) / OUNCE_TO_GRAM

    return round(gram_gold, 2)


def get_gold_price() -> float | None:

    try:
        response = requests.get(
            GOLD_API_URL,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        gold_price = float(data["price"])

        logger.info("Ons altın fiyatı başarıyla alındı.")

        return gold_price

    except requests.exceptions.RequestException as error:
        logger.error(f"Altın API Hatası: {error}")
        return None


def get_market_data() -> dict | None:
    
    exchange_rates = get_exchange_rates()
    ounce_price = get_gold_price()

    if exchange_rates is None or ounce_price is None:
        return None

    market_data = {
        "usd_try": exchange_rates["usd_try"],
        "eur_try": exchange_rates["eur_try"],
        "gbp_try": exchange_rates["gbp_try"],
        "gold_ounce": round(ounce_price, 2),
        "gold_gram": calculate_gram_gold(
            ounce_price,
            exchange_rates["usd_try"],
        ),
        "timestamp": exchange_rates["timestamp"],
    }

    logger.info("Piyasa verileri başarıyla oluşturuldu.")

    return market_data


if __name__ == "__main__":
    market_data = get_market_data()

    if market_data:
        print(market_data)