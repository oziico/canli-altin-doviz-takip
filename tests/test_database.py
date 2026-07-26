import pytest

import database


@pytest.fixture
def temporary_database(tmp_path, monkeypatch):
    """
    Her test için geçici bir SQLite veritabanı oluşturur.
    """
    test_database_path = tmp_path / "test_market_data.db"

    monkeypatch.setattr(
        database,
        "DATABASE_NAME",
        str(test_database_path),
    )

    database.create_table()

    return test_database_path


def sample_market_data():
    return {
        "timestamp": "2026-07-27 12:00:00",
        "usd_try": 40.12,
        "eur_try": 46.35,
        "gbp_try": 53.44,
        "gold_ounce": 2500.55,
        "gold_gram": 3220.75,
    }


def test_insert_market_data(temporary_database):
    database.insert_market_data(sample_market_data())

    latest = database.get_latest_market_data()

    assert latest is not None
    assert latest["usd_try"] == pytest.approx(40.12)
    assert latest["eur_try"] == pytest.approx(46.35)
    assert latest["gbp_try"] == pytest.approx(53.44)
    assert latest["gold_ounce"] == pytest.approx(2500.55)
    assert latest["gold_gram"] == pytest.approx(3220.75)


def test_get_latest_market_data_empty_database(temporary_database):
    latest = database.get_latest_market_data()

    assert latest is None


def test_get_all_market_data_empty_database(temporary_database):
    data = database.get_all_market_data()

    assert data == []


def test_get_all_market_data(temporary_database):
    database.insert_market_data(sample_market_data())

    second = sample_market_data()
    second["timestamp"] = "2026-07-27 12:05:00"
    second["usd_try"] = 40.50

    database.insert_market_data(second)

    data = database.get_all_market_data()

    assert len(data) == 2
    assert data[0]["usd_try"] == pytest.approx(40.12)
    assert data[1]["usd_try"] == pytest.approx(40.50)


def test_get_current_value_existing_metric(temporary_database):
    database.insert_market_data(sample_market_data())

    value = database.get_current_value("usd_try")

    assert value == pytest.approx(40.12)


def test_get_current_value_invalid_metric(temporary_database):
    database.insert_market_data(sample_market_data())

    value = database.get_current_value("invalid_metric")

    assert value is None


def test_get_current_value_without_data(temporary_database):
    value = database.get_current_value("usd_try")

    assert value is None


def test_latest_market_data_returns_last_inserted(temporary_database):
    database.insert_market_data(sample_market_data())

    second = sample_market_data()
    second["timestamp"] = "2026-07-27 13:00:00"
    second["usd_try"] = 41.00

    database.insert_market_data(second)

    latest = database.get_latest_market_data()

    assert latest["usd_try"] == pytest.approx(41.00)


def test_create_table_can_be_called_multiple_times(temporary_database):
    database.create_table()
    database.create_table()
    database.create_table()

    assert True


def test_insert_multiple_market_records(temporary_database):
    for i in range(5):
        data = sample_market_data()
        data["timestamp"] = f"2026-07-27 12:0{i}:00"
        data["usd_try"] = 40 + i

        database.insert_market_data(data)

    rows = database.get_all_market_data()

    assert len(rows) == 5
    assert rows[-1]["usd_try"] == pytest.approx(44)