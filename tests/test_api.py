import requests

import api


class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(
                f"HTTP {self.status_code}"
            )


def test_calculate_gram_gold(monkeypatch):
    monkeypatch.setattr(api, "OUNCE_TO_GRAM", 31.1035)

    result = api.calculate_gram_gold(
        ounce_price=2000.0,
        usd_try=40.0,
    )

    expected = round((2000.0 * 40.0) / 31.1035, 2)

    assert result == expected


def test_get_forex_price_success(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse(
            {
                "values": [
                    {
                        "datetime": "2026-07-26 12:00:00",
                        "close": "40.1256",
                    }
                ]
            }
        )

    monkeypatch.setattr(api, "TWELVE_DATA_API_KEY", "test-key")
    monkeypatch.setattr(api.requests, "get", mock_get)

    result = api.get_forex_price("USD/TRY")

    assert result == 40.1256


def test_get_forex_price_without_api_key(monkeypatch):
    monkeypatch.setattr(api, "TWELVE_DATA_API_KEY", "")

    result = api.get_forex_price("USD/TRY")

    assert result is None


def test_get_forex_price_api_error(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse(
            {
                "status": "error",
                "message": "Invalid API key",
            }
        )

    monkeypatch.setattr(api, "TWELVE_DATA_API_KEY", "test-key")
    monkeypatch.setattr(api.requests, "get", mock_get)

    result = api.get_forex_price("USD/TRY")

    assert result is None


def test_get_forex_price_without_values(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse({})

    monkeypatch.setattr(api, "TWELVE_DATA_API_KEY", "test-key")
    monkeypatch.setattr(api.requests, "get", mock_get)

    result = api.get_forex_price("USD/TRY")

    assert result is None


def test_get_forex_price_invalid_close(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse(
            {
                "values": [
                    {
                        "datetime": "2026-07-26 12:00:00",
                        "close": "gecersiz",
                    }
                ]
            }
        )

    monkeypatch.setattr(api, "TWELVE_DATA_API_KEY", "test-key")
    monkeypatch.setattr(api.requests, "get", mock_get)

    result = api.get_forex_price("USD/TRY")

    assert result is None


def test_get_forex_price_connection_error(monkeypatch):
    def mock_get(*args, **kwargs):
        raise requests.exceptions.ConnectionError(
            "Bağlantı kurulamadı"
        )

    monkeypatch.setattr(api, "TWELVE_DATA_API_KEY", "test-key")
    monkeypatch.setattr(api.requests, "get", mock_get)

    result = api.get_forex_price("USD/TRY")

    assert result is None


def test_get_exchange_rates_success(monkeypatch):
    prices = {
        "USD/TRY": 40.123456,
        "EUR/TRY": 46.234567,
        "GBP/TRY": 53.345678,
    }

    monkeypatch.setattr(
        api,
        "get_forex_price",
        lambda symbol: prices[symbol],
    )

    monkeypatch.setattr(
        api,
        "current_timestamp",
        lambda: "2026-07-26 12:00:00",
    )

    result = api.get_exchange_rates()

    assert result == {
        "usd_try": 40.1235,
        "eur_try": 46.2346,
        "gbp_try": 53.3457,
        "timestamp": "2026-07-26 12:00:00",
    }


def test_get_exchange_rates_returns_none_when_rate_missing(
    monkeypatch,
):
    prices = {
        "USD/TRY": 40.0,
        "EUR/TRY": None,
        "GBP/TRY": 53.0,
    }

    monkeypatch.setattr(
        api,
        "get_forex_price",
        lambda symbol: prices[symbol],
    )

    result = api.get_exchange_rates()

    assert result is None


def test_get_gold_price_success(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse({"price": "2500.75"})

    monkeypatch.setattr(api.requests, "get", mock_get)

    result = api.get_gold_price()

    assert result == 2500.75


def test_get_gold_price_missing_price(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse({})

    monkeypatch.setattr(api.requests, "get", mock_get)

    result = api.get_gold_price()

    assert result is None


def test_get_gold_price_invalid_price(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse({"price": "gecersiz"})

    monkeypatch.setattr(api.requests, "get", mock_get)

    result = api.get_gold_price()

    assert result is None


def test_get_gold_price_connection_error(monkeypatch):
    def mock_get(*args, **kwargs):
        raise requests.exceptions.Timeout(
            "İstek zaman aşımına uğradı"
        )

    monkeypatch.setattr(api.requests, "get", mock_get)

    result = api.get_gold_price()

    assert result is None


def test_get_market_data_success(monkeypatch):
    monkeypatch.setattr(
        api,
        "get_exchange_rates",
        lambda: {
            "usd_try": 40.0,
            "eur_try": 46.0,
            "gbp_try": 53.0,
            "timestamp": "2026-07-26 12:00:00",
        },
    )

    monkeypatch.setattr(
        api,
        "get_gold_price",
        lambda: 2500.0,
    )

    monkeypatch.setattr(
        api,
        "calculate_gram_gold",
        lambda ounce_price, usd_try: 3215.0,
    )

    result = api.get_market_data()

    assert result == {
        "usd_try": 40.0,
        "eur_try": 46.0,
        "gbp_try": 53.0,
        "timestamp": "2026-07-26 12:00:00",
        "gold_ounce": 2500.0,
        "gold_gram": 3215.0,
    }


def test_get_market_data_returns_none_when_forex_missing(
    monkeypatch,
):
    monkeypatch.setattr(
        api,
        "get_exchange_rates",
        lambda: None,
    )

    monkeypatch.setattr(
        api,
        "get_gold_price",
        lambda: 2500.0,
    )

    result = api.get_market_data()

    assert result is None


def test_get_market_data_returns_none_when_gold_missing(
    monkeypatch,
):
    monkeypatch.setattr(
        api,
        "get_exchange_rates",
        lambda: {
            "usd_try": 40.0,
            "eur_try": 46.0,
            "gbp_try": 53.0,
            "timestamp": "2026-07-26 12:00:00",
        },
    )

    monkeypatch.setattr(
        api,
        "get_gold_price",
        lambda: None,
    )

    result = api.get_market_data()

    assert result is None