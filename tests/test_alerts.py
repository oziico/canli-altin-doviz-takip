import pytest

import database
from scheduler import is_alert_triggered


@pytest.fixture
def temporary_database(tmp_path, monkeypatch):
    """
    Her test için geçici ve bağımsız bir SQLite veritabanı oluşturur.
    Gerçek market_data.db dosyasını değiştirmez.
    """
    test_database_path = tmp_path / "test_market_data.db"

    monkeypatch.setattr(
        database,
        "DATABASE_NAME",
        str(test_database_path),
    )

    database.create_table()

    return test_database_path


def test_above_condition_is_triggered():
    assert is_alert_triggered(
        current_value=35.0,
        condition=">",
        target_value=34.0,
    )


def test_above_condition_is_not_triggered():
    assert not is_alert_triggered(
        current_value=33.0,
        condition=">",
        target_value=34.0,
    )


def test_below_condition_is_triggered():
    assert is_alert_triggered(
        current_value=33.0,
        condition="<",
        target_value=34.0,
    )


def test_below_condition_is_not_triggered():
    assert not is_alert_triggered(
        current_value=35.0,
        condition="<",
        target_value=34.0,
    )


def test_equal_value_does_not_trigger_strict_conditions():
    assert not is_alert_triggered(
        current_value=34.0,
        condition=">",
        target_value=34.0,
    )

    assert not is_alert_triggered(
        current_value=34.0,
        condition="<",
        target_value=34.0,
    )


def test_invalid_condition_returns_false():
    assert not is_alert_triggered(
        current_value=35.0,
        condition="invalid",
        target_value=34.0,
    )


def test_insert_alert(temporary_database):
    database.insert_alert(
        metric="usd_try",
        condition=">",
        target_value=40.0,
    )

    alerts = database.get_active_alerts()

    assert len(alerts) == 1
    assert alerts[0]["metric"] == "usd_try"
    assert alerts[0]["condition"] == ">"
    assert alerts[0]["target_value"] == pytest.approx(40.0)


def test_alert_exists(temporary_database):
    database.insert_alert(
        metric="eur_try",
        condition="<",
        target_value=35.0,
    )

    exists = database.alert_exists(
        metric="eur_try",
        condition="<",
        target_value=35.0,
    )

    assert exists is True


def test_alert_does_not_exist(temporary_database):
    exists = database.alert_exists(
        metric="gbp_try",
        condition=">",
        target_value=50.0,
    )

    assert exists is False


def test_delete_alert(temporary_database):
    database.insert_alert(
        metric="gold_gram",
        condition=">",
        target_value=5000.0,
    )

    alerts = database.get_active_alerts()
    alert_id = alerts[0]["id"]

    database.delete_alert(alert_id)

    remaining_alerts = database.get_active_alerts()

    assert remaining_alerts == []


def test_mark_alert_as_triggered(temporary_database):
    database.insert_alert(
        metric="gold_ounce",
        condition=">",
        target_value=3000.0,
    )

    alerts = database.get_active_alerts()
    alert_id = alerts[0]["id"]

    database.mark_alert_as_triggered(alert_id)

    active_alerts = database.get_active_alerts()

    assert active_alerts == []


def test_insert_alert_history(temporary_database):
    database.insert_alert(
        metric="usd_try",
        condition=">",
        target_value=40.0,
    )

    alerts = database.get_active_alerts()
    alert_id = alerts[0]["id"]

    database.insert_alert_history(
        alert_id=alert_id,
        metric="usd_try",
        condition=">",
        target_value=40.0,
        current_value=41.0,
    )

    history = database.get_alert_history()

    assert len(history) == 1
    assert history[0]["alert_id"] == alert_id
    assert history[0]["metric"] == "usd_try"
    assert history[0]["condition"] == ">"
    assert history[0]["target_value"] == pytest.approx(40.0)
    assert history[0]["current_value"] == pytest.approx(41.0)


def test_get_last_triggered_alert(temporary_database):
    database.insert_alert(
        metric="eur_try",
        condition="<",
        target_value=35.0,
    )

    alerts = database.get_active_alerts()
    alert_id = alerts[0]["id"]

    database.insert_alert_history(
        alert_id=alert_id,
        metric="eur_try",
        condition="<",
        target_value=35.0,
        current_value=34.5,
    )

    last_alert = database.get_last_triggered_alert()

    assert last_alert is not None
    assert last_alert["alert_id"] == alert_id
    assert last_alert["metric"] == "eur_try"
    assert last_alert["condition"] == "<"
    assert last_alert["target_value"] == pytest.approx(35.0)
    assert last_alert["current_value"] == pytest.approx(34.5)