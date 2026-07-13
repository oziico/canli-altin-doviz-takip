from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from database import get_all_market_data, get_latest_market_data

st.set_page_config(
    page_title="Canlı Altın ve Döviz Takip",
    page_icon="📈",
    layout="wide",
)

st_autorefresh(interval=30_000, key="refresh")

st.title("📈 Canlı Altın ve Döviz Takip Sistemi")
st.caption("Canlı altın ve döviz verileri SQLite veritabanından okunmaktadır.")

latest = get_latest_market_data()

if latest is None:
    st.warning("Henüz veritabanında veri bulunmuyor.")
    st.stop()

st.subheader("📅 Son Güncelleme")
st.write(latest["timestamp"])

col1, col2 = st.columns(2)

with col1:
    st.subheader("💵 Döviz")

    st.metric("USD / TRY", f"{latest['usd_try']:.4f}")
    st.metric("EUR / TRY", f"{latest['eur_try']:.4f}")
    st.metric("GBP / TRY", f"{latest['gbp_try']:.4f}")

with col2:
    st.subheader("🥇 Altın")

    st.metric("Ons Altın ($)", f"{latest['gold_ounce']:.2f}")
    st.metric("Gram Altın (TL)", f"{latest['gold_gram']:.2f}")

st.divider()

data = get_all_market_data()
df = pd.DataFrame(data)

if not df.empty:

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    st.sidebar.header("⚙️ Filtreler")

    period = st.sidebar.selectbox(
        "📅 Veri Aralığı",
        (
            "Tüm Veriler",
            "Son 1 Saat",
            "Son 24 Saat",
            "Son 7 Gün",
        ),
    )

    now = datetime.now()

    if period == "Son 1 Saat":
        df = df[df["timestamp"] >= now - timedelta(hours=1)]

    elif period == "Son 24 Saat":
        df = df[df["timestamp"] >= now - timedelta(days=1)]

    elif period == "Son 7 Gün":
        df = df[df["timestamp"] >= now - timedelta(days=7)]

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📈 Gram Altın Grafiği")

        fig = px.line(
            df,
            x="timestamp",
            y="gold_gram",
            markers=True,
            title="Gram Altın (TL)",
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        st.subheader("💵 USD / TRY Grafiği")

        fig = px.line(
            df,
            x="timestamp",
            y="usd_try",
            markers=True,
            title="USD / TRY",
        )

        st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("📋 Veritabanındaki Tüm Kayıtlar")
st.dataframe(df, use_container_width=True)

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Verileri CSV Olarak İndir",
    data=csv,
    file_name="market_data.csv",
    mime="text/csv",
)