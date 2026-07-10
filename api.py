"""
api.py canlı altın ve döviz verilerini ücretsiz API'lerden çeker.
"""
import requests
from datetime import datetime


BASE_URL = "https://api.frankfurter.dev/v1/latest"


def get_exchange_rates():
    try:
        response = requests.get(
            BASE_URL,
            params={
                "base": "TRY",
                "symbols": "USD,EUR,GBP"
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        rates = data["rates"]

        exchange_rates = {
            "usd_try": round(1 / rates["USD"], 4),
            "eur_try": round(1 / rates["EUR"], 4),
            "gbp_try": round(1 / rates["GBP"], 4),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return exchange_rates

    except requests.exceptions.RequestException as e:
        print(f"API Hatası: {e}")
        return None
    
if __name__ == "__main__":
    print(get_exchange_rates())