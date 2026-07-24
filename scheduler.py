import logging
import time

from apscheduler.schedulers.background import BackgroundScheduler

from api import get_market_data
from database import (
    create_table,
    insert_market_data,
    get_latest_market_data,
    get_active_alerts,
    mark_alert_as_triggered,
    insert_alert_history,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

def check_alerts() -> None:
    """
    Aktif alarmları kontrol eder.
    """

    latest = get_latest_market_data()

    if latest is None:
        return

    alerts = get_active_alerts()

    for alert in alerts:

        metric = alert["metric"]
        condition = alert["condition"]
        target = alert["target_value"]

        current = latest[metric]

        triggered = False

        if condition == ">":
            triggered = current > target

        elif condition == "<":
            triggered = current < target

        if triggered:

            mark_alert_as_triggered(alert["id"])

            insert_alert_history(
                alert["id"],
                metric,
                condition,
                target,
                current,
            )

            logger.info(
                f"ALARM! {metric} = {current}"
            )

def update_market_data() -> None:
    """
    API'den verileri alır ve veritabanına kaydeder.
    """
    market_data = get_market_data()

    if market_data:
        insert_market_data(market_data)
        check_alerts()
        logger.info("Yeni piyasa verisi kaydedildi.")
    else:
        logger.warning("Piyasa verisi alınamadı.")


def start_scheduler() -> None:
    """
    Scheduler'ı başlatır.
    """
    create_table()

    logger.info("İlk piyasa verisi alınıyor...")
    update_market_data()

    scheduler = BackgroundScheduler()

    scheduler.add_job(
        update_market_data,
        trigger="interval",
        minutes=1,
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