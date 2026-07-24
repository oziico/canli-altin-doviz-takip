import streamlit as st

from database import get_last_triggered_alert


ALERT_NAME_MAP = {
    "usd_try": "USD / TRY",
    "eur_try": "EUR / TRY",
    "gbp_try": "GBP / TRY",
    "gold_ounce": "Ons Altın ($)",
    "gold_gram": "Gram Altın (TL)",
}


def initialize_alert_state(last_alert: dict | None) -> None:
    """
    Alarm sistemi için gerekli session_state
    değişkenlerini güvenli şekilde oluşturur.
    """

    if "alert_system_initialized" not in st.session_state:
        st.session_state.alert_system_initialized = True

        # Uygulama açılmadan önce oluşmuş eski alarmı
        # başlangıç noktası kabul et.
        st.session_state.last_seen_alert_id = (
            last_alert["id"]
            if last_alert is not None
            else None
        )

    if "visible_alert_id" not in st.session_state:
        st.session_state.visible_alert_id = None

    if "last_sound_alert_id" not in st.session_state:
        st.session_state.last_sound_alert_id = None


def get_new_alert() -> dict | None:
    """
    Veritabanındaki son tetiklenen alarmı kontrol eder.

    Uygulama açıkken yeni bir alarm tetiklendiyse
    görünür alarm olarak işaretler ve ses durumunu sıfırlar.
    """

    last_alert = get_last_triggered_alert()

    initialize_alert_state(last_alert)

    if (
        last_alert is not None
        and last_alert["id"]
        != st.session_state.last_seen_alert_id
    ):
        # Yeni alarm bulundu
        st.session_state.last_seen_alert_id = last_alert["id"]

        # Alarm kartını görünür yap
        st.session_state.visible_alert_id = last_alert["id"]

        # Yeni alarm için sesin tekrar çalabilmesini sağla
        st.session_state.last_sound_alert_id = None

    return last_alert


def should_show_alert(last_alert: dict | None) -> bool:
    """
    Alarm kartının gösterilip gösterilmeyeceğini belirler.
    """

    return (
        last_alert is not None
        and st.session_state.visible_alert_id
        == last_alert["id"]
    )


def dismiss_alert() -> None:
    """
    Görünür alarm kartını kapatır.
    """

    st.session_state.visible_alert_id = None


def should_play_alarm_sound(alert_id: int) -> bool:
    """
    Aynı alarm için sesin tekrar tekrar
    çalmasını engeller.
    """

    return (
        st.session_state.last_sound_alert_id
        != alert_id
    )


def mark_alarm_sound_as_played(alert_id: int) -> None:
    """
    Alarm sesinin çalındığını session_state'e kaydeder.
    """

    st.session_state.last_sound_alert_id = alert_id