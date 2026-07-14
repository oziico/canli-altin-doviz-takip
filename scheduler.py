"""
scheduler.py

Belirli aralıklarla piyasa verilerini çekip veritabanına kaydeder.
"""

import logging
import time

from apscheduler.schedulers.background import BackgroundScheduler

from api import get_market_data
from database import create_table, insert_market_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def update_market_data() -> None:
    """
    API'den verileri alır ve veritabanına kaydeder.
    """
    market_data = get_market_data()

    if market_data:
        insert_market_data(market_data)
        logger.info("Yeni piyasa verisi kaydedildi.")
    else:
        logger.warning("Piyasa verisi alınamadı.")


def start_scheduler() -> None:
    """
    Scheduler'ı başlatır.
    """
    create_table()

    # İlk veriyi hemen kaydet
    logger.info("İlk piyasa verisi alınıyor...")
    update_market_data()

    scheduler = BackgroundScheduler()

    scheduler.add_job(
        update_market_data,
        trigger="interval",
        minutes=5,
    )

    scheduler.start()

    logger.info("Scheduler başlatıldı. Her 5 dakikada bir veri kaydedilecek.")

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler durduruldu.")


if __name__ == "__main__":
    start_scheduler()