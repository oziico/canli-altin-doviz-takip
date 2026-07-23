import logging
import sqlite3
from datetime import datetime
from api import get_market_data

DATABASE_NAME = "market_data.db"

def create_connection() -> sqlite3.Connection:
    return sqlite3.connect(
        DATABASE_NAME,
        check_same_thread=False
    )

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)



def create_table() -> None:
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            usd_try REAL NOT NULL,
            eur_try REAL NOT NULL,
            gbp_try REAL NOT NULL,
            gold_ounce REAL NOT NULL,
            gold_gram REAL NOT NULL
        )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metric TEXT NOT NULL,
        condition TEXT NOT NULL,
        target_value REAL NOT NULL,
        is_triggered INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    )
""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alert_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alert_id INTEGER NOT NULL,
        metric TEXT NOT NULL,
        condition TEXT NOT NULL,
        target_value REAL NOT NULL,
        current_value REAL NOT NULL,
        triggered_at TEXT NOT NULL
    )
""")

    connection.commit()
    connection.close()

    logger.info("Veritabanı tabloları hazır.")

create_table()


def insert_market_data(data: dict) -> None:
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO market_data (
            timestamp,
            usd_try,
            eur_try,
            gbp_try,
            gold_ounce,
            gold_gram
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["timestamp"],
        data["usd_try"],
        data["eur_try"],
        data["gbp_try"],
        data["gold_ounce"],
        data["gold_gram"],
    ))

    connection.commit()
    connection.close()

    logger.info("Piyasa verisi başarıyla kaydedildi.")


def get_latest_market_data() -> dict | None:
    connection = create_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM market_data
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)


def get_all_market_data() -> list[dict]:
    connection = create_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM market_data
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


def insert_alert(metric: str, condition: str, target_value: float) -> None:
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO alerts (
        metric,
        condition,
        target_value,
        is_triggered,
        created_at
    )
    VALUES (?, ?, ?, 0, ?)
""", (
    metric,
    condition,
    target_value,
    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
))

    connection.commit()
    connection.close()


def get_active_alerts() -> list[dict]:
    connection = create_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM alerts
        WHERE is_triggered = 0
    """)

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]

def alert_exists(metric: str, condition: str, target_value: float) -> bool:
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT 1
        FROM alerts
        WHERE metric = ?
          AND condition = ?
          AND target_value = ?
          AND is_triggered = 0
        LIMIT 1
    """, (metric, condition, target_value))

    exists = cursor.fetchone() is not None

    connection.close()

    return exists

def get_all_alerts() -> list[dict]:
    connection = create_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM alerts
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


def mark_alert_as_triggered(alert_id: int) -> None:
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE alerts
        SET is_triggered = 1
        WHERE id = ?
    """, (alert_id,))

    connection.commit()
    connection.close()


def delete_alert(alert_id: int) -> None:
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM alerts
        WHERE id = ?
    """, (alert_id,))

    connection.commit()
    connection.close()


def insert_alert_history(
    alert_id: int,
    metric: str,
    condition: str,
    target_value: float,
    current_value: float,
) -> None:

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO alert_history (
            alert_id,
            metric,
            condition,
            target_value,
            current_value,
            triggered_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        alert_id,
        metric,
        condition,
        target_value,
        current_value,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ))

    connection.commit()
    connection.close()


def get_alert_history() -> list[dict]:

    connection = create_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM alert_history
        ORDER BY triggered_at DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]

def get_last_triggered_alert() -> dict | None:

    connection = create_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM alert_history
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)

def get_current_value(metric: str) -> float | None:
    """
    İstenen varlığın en güncel değerini döndürür.
    """

    latest = get_latest_market_data()

    if latest is None:
        return None

    return latest.get(metric)

if __name__ == "__main__":
    market_data = get_market_data()

    if market_data:
        insert_market_data(market_data)

        latest = get_latest_market_data()

        print(latest)