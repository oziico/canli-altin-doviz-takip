import streamlit as st

def show_alarm_notification(alert: dict):

    if alert is None:
        return

    st.info(
        f"""
🔔 Alarm Tetiklendi!

{alert["metric"]}

{alert["current_value"]:.4f} {alert["condition"]} {alert["target_value"]:.4f}
"""
    )