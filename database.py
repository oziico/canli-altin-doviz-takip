import logging
import sqlite3

from api import get_market_data

DATABASE_NAME = "market_data.db"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def create_connection() -> sqlite3.Connection:
    
    return sqlite3.connect(DATABASE_NAME)


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

    connection.commit()
    connection.close()

    logger.info("market_data tablosu hazır.")


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


if __name__ == "__main__":
    create_table()

    market_data = get_market_data()

    if market_data:
        insert_market_data(market_data)

        latest = get_latest_market_data()

        print(latest)