import logging
import time

from apscheduler.schedulers.background import BackgroundScheduler

from api import get_market_data
from database import (
    get_active_alerts,
    get_latest_market_data,
    insert_alert_history,
    insert_market_data,
    mark_alert_as_triggered,
)


UPDATE_INTERVAL_MINUTES = 5
MAIN_LOOP_SLEEP_SECONDS = 1

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def is_alert_triggered(
    condition: str,
    current_value: float,
    target_value: float,
) -> bool:
    """Alarm koşulunun gerçekleşip gerçekleşmediğini kontrol eder."""
    if condition == ">":
        return current_value > target_value

    if condition == "<":
        return current_value < target_value

    logger.warning("Geçersiz alarm koşulu: %s", condition)
    return False


def check_alerts() -> None:
    """Aktif alarmları en güncel piyasa verisine göre kontrol eder."""
    latest = get_latest_market_data()

    if latest is None:
        logger.warning("Alarm kontrolü için piyasa verisi bulunamadı.")
        return

    alerts = get_active_alerts()

    for alert in alerts:
        metric = alert["metric"]
        condition = alert["condition"]
        target_value = alert["target_value"]
        current_value = latest.get(metric)

        if current_value is None:
            logger.warning("Piyasa verisinde geçersiz metrik: %s", metric)
            continue

        if not is_alert_triggered(
            condition,
            current_value,
            target_value,
        ):
            continue

        mark_alert_as_triggered(alert["id"])

        insert_alert_history(
            alert["id"],
            metric,
            condition,
            target_value,
            current_value,
        )

        logger.info(
            "ALARM TETİKLENDİ: %s %.4f %s %.4f",
            metric,
            current_value,
            condition,
            target_value,
        )


def update_market_data() -> None:
    """API verilerini alır, veritabanına kaydeder ve alarmları kontrol eder."""
    market_data = get_market_data()

    if not market_data:
        logger.warning("Piyasa verisi alınamadı.")
        return

    insert_market_data(market_data)
    check_alerts()

    logger.info("Yeni piyasa verisi kaydedildi.")


def start_scheduler() -> None:
    """Piyasa verisi güncelleme zamanlayıcısını başlatır."""
    logger.info("İlk piyasa verisi alınıyor...")
    update_market_data()

    scheduler = BackgroundScheduler()

    scheduler.add_job(
        update_market_data,
        trigger="interval",
        minutes=UPDATE_INTERVAL_MINUTES,
        max_instances=1,
        coalesce=True,
    )

    scheduler.start()

    logger.info(
        "Scheduler başlatıldı. Her %s dakikada bir veri kaydedilecek.",
        UPDATE_INTERVAL_MINUTES,
    )

    try:
        while True:
            time.sleep(MAIN_LOOP_SLEEP_SECONDS)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler durduruldu.")


if __name__ == "__main__":
    start_scheduler()