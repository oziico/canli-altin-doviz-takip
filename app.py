import os
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st

from database import get_all_market_data, get_latest_market_data

st.set_page_config(
    page_title="Canlı Altın ve Döviz Takip Sistemi",
    page_icon="📈",
    layout="wide",
)

def show_statistics(df, column, suffix):
    maximum = df[column].max()
    minimum = df[column].min()
    average = df[column].mean()

    col1, col2, col3 = st.columns([1, 1, 1], gap="medium")

    precision = ".4f" if column in ['usd_try', 'eur_try', 'gbp_try'] else ".2f"
    
    val_max = f"{maximum:{precision}} {suffix}"
    val_min = f"{minimum:{precision}} {suffix}"
    val_avg = f"{average:{precision}} {suffix}"

    card_style = (
        "display: flex; "
        "flex-direction: column; "
        "justify-content: space-evenly; "
        "align-items: center; "
        "height: 110px; "
        "border-radius: 12px; "
        "padding: 16px 12px; "
        "text-align: center; "
        "box-sizing: border-box;"
    )

    with col1:
        st.markdown(f"""
        <div style="{card_style} background: #1e352f;">
            <h5 style="margin: 0; color: #4ade80; font-size: 14px; font-weight: 600; line-height: 1.2;">📈 En Yüksek</h5>
            <h3 style="margin: 0; font-size: 18px; font-weight: bold; color: #f1f5f9; line-height: 1.2;">{val_max}</h3>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="{card_style} background: #3b1d1d;">
            <h5 style="margin: 0; color: #f87171; font-size: 14px; font-weight: 600; line-height: 1.2;">⬇️ En Düşük</h5>
            <h3 style="margin: 0; font-size: 18px; font-weight: bold; color: #f1f5f9; line-height: 1.2;">{val_min}</h3>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="{card_style} background: #1c3154;">
            <h5 style="margin: 0; color: #60a5fa; font-size: 14px; font-weight: 600; line-height: 1.2;">📊 Ortalama</h5>
            <h3 style="margin: 0; font-size: 18px; font-weight: bold; color: #f1f5f9; line-height: 1.2;">{val_avg}</h3>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<style>
.block-container{
    padding-top:2rem;
}
.gold-card{
    background:#FFF9E8;
}
.currency-card{
    background:#F4F8FF;
}
.vertical-divider{
    border-left:1px solid #D8D8D8;
    height:100%;
}
</style>
""", unsafe_allow_html=True)


st.title("📈 Canlı Altın ve Döviz Takip Sistemi")
st.caption("Canlı altın ve döviz verileri SQLite veritabanından okunmaktadır.")

latest = get_latest_market_data()

if latest is None:
    st.warning("Henüz veritabanında veri bulunmuyor.")
    st.stop()

formatted_time = pd.to_datetime(latest["timestamp"]).strftime("%d.%m.%Y %H:%M:%S")

st.markdown(f"""
<div style="
    background: #1E293B;
    padding: 11px 16px;
    border-radius: 8px;
    border-left: 4px solid #FFD700;
    display: flex;
    align-items: center;
    gap: 8px;
    box-sizing: border-box;
    height: 42px;
    margin-bottom: 25px;
">
    <span style="font-size: 14px; color: #94A3B8; margin: 0;">🕒 Son Güncelleme:</span>
    <strong style="font-size: 14px; color: #F1F5F9; margin: 0;">{formatted_time}</strong>
</div>
""", unsafe_allow_html=True)


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

    if df.empty:
        st.info("Seçilen zaman aralığında veri bulunmuyor.")
    else:
        st.header("🥇 Altın Analizi")
        gold_col1, divider, gold_col2 = st.columns([1, 0.03, 1])

        with divider:
            st.markdown(
                """
                <div style="
                    border-left:1px solid rgba(255,255,255,0.20);
                    height:620px;
                    margin:auto;
                "></div>
                """,
                unsafe_allow_html=True,
            )

        with gold_col1:
            st.markdown("### 📈 Gram Altın Grafiği")
            fig = px.line(
                df,
                x="timestamp",
                y="gold_gram",
                markers=True,
                title="Gram Altın (TL)",
                color_discrete_sequence=["gold"],
            )
            fig.update_traces(line=dict(width=3), marker=dict(size=8))
            fig.add_annotation(
                x=df["timestamp"].iloc[-1],
                y=df["gold_gram"].iloc[-1],
                text=f"{df['gold_gram'].iloc[-1]:.2f}",
                showarrow=True,
                arrowhead=2,
                bgcolor="gold",
            )
            fig.update_layout(
                height=400,
                template="plotly_dark",
                margin=dict(l=10, r=10, t=40, b=10),
            )
            st.plotly_chart(fig, width="stretch")
            show_statistics(df, "gold_gram", "TL")

        with gold_col2:
            st.subheader("📈 Ons Altın Grafiği")
            fig = px.line(
                df,
                x="timestamp",
                y="gold_ounce",
                markers=True,
                title="Ons Altın ($)",
                color_discrete_sequence=["orange"],
            )
            fig.update_traces(line=dict(width=3), marker=dict(size=8))
            fig.update_layout(
                height=400,
                template="plotly_dark",
                margin=dict(l=10, r=10, t=40, b=10),
            )
            fig.add_annotation(
                x=df["timestamp"].iloc[-1],
                y=df["gold_ounce"].iloc[-1],
                text=f"{df['gold_ounce'].iloc[-1]:.2f}",
                showarrow=True,
                arrowhead=2,
                bgcolor="orange",
            )
            st.plotly_chart(fig, width="stretch")
            show_statistics(df, "gold_ounce", "$")

        st.divider()

        st.header("💵 Döviz Analizi")
        usd_col, divider1, eur_col, divider2, gbp_col = st.columns([1, 0.03, 1, 0.03, 1])

        with divider1:
            st.markdown(
                """
                <div style="
                    border-left:1px solid rgba(255,255,255,0.20);
                    height:620px;
                    margin:auto;
                "></div>
                """,
                unsafe_allow_html=True,
            )

        with divider2:
            st.markdown(
                """
                <div style="
                    border-left:1px solid rgba(255,255,255,0.20);
                    height:620px;
                    margin:auto;
                "></div>
                """,
                unsafe_allow_html=True,
            )

        with usd_col:
            st.subheader("💵 USD / TRY Grafiği")
            fig = px.line(
                df,
                x="timestamp",
                y="usd_try",
                markers=True,
                title="USD / TRY",
                color_discrete_sequence=["green"],
            )
            fig.update_traces(line=dict(width=3), marker=dict(size=8))
            fig.update_layout(
                height=400,
                template="plotly_dark",
                margin=dict(l=10,r=10,t=40,b=10),
            )
            fig.add_annotation(
                x=df["timestamp"].iloc[-1],
                y=df["usd_try"].iloc[-1],
                text=f"{df['usd_try'].iloc[-1]:.4f}",
                showarrow=True,
                arrowhead=2,
                bgcolor="green",
            )
            st.plotly_chart(fig, width="stretch")
            show_statistics(df, "usd_try", "TL")

        with eur_col:
            st.subheader("💶 EUR / TRY Grafiği")
            fig = px.line(
                df,
                x="timestamp",
                y="eur_try",
                markers=True,
                title="EUR / TRY",
                color_discrete_sequence=["royalblue"],
            )
            fig.update_traces(line=dict(width=3), marker=dict(size=8))
            fig.update_layout(
                height=400,
                template="plotly_dark",
                margin=dict(l=10,r=10,t=40,b=10),
            )
            fig.add_annotation(
                x=df["timestamp"].iloc[-1],
                y=df["eur_try"].iloc[-1],
                text=f"{df['eur_try'].iloc[-1]:.4f}",
                showarrow=True,
                arrowhead=2,
                bgcolor="royalblue",
            )
            st.plotly_chart(fig, width="stretch")
            show_statistics(df, "eur_try", "TL")

        with gbp_col:
            st.subheader("💷 GBP / TRY Grafiği")
            fig = px.line(
                df,
                x="timestamp",
                y="gbp_try",
                markers=True,
                title="GBP / TRY",
                color_discrete_sequence=["purple"],
            )
            fig.update_traces(line=dict(width=3), marker=dict(size=8))
            fig.update_layout(
                height=400,
                template="plotly_dark",
                margin=dict(l=10,r=10,t=40,b=10),
            )
            fig.add_annotation(
                x=df["timestamp"].iloc[-1],
                y=df["gbp_try"].iloc[-1],
                text=f"{df['gbp_try'].iloc[-1]:.4f}",
                showarrow=True,
                arrowhead=2,
                bgcolor="purple",
            )
            st.plotly_chart(fig, width="stretch")
            show_statistics(df, "gbp_try", "TL")

st.divider()

st.subheader("📋 Veritabanındaki Tüm Kayıtlar")

df_table = df.sort_values("timestamp", ascending=False)
st.dataframe(df_table, width="stretch")


#CSV İNDİRME

temp_df = df_table.copy()
if 'timestamp' in temp_df.columns:
    temp_df['timestamp'] = temp_df['timestamp'].astype(str)

csv_string = temp_df.to_csv(index=False)

import urllib.parse
temp_df = df_table.copy()
if 'timestamp' in temp_df.columns:
    temp_df['timestamp'] = temp_df['timestamp'].astype(str)

csv_string = temp_df.to_csv(index=False)

csv_encoded = urllib.parse.quote(csv_string)
data_uri = f"data:text/csv;charset=utf-8-sig,{csv_encoded}"

st.markdown(f"""
<a href="{data_uri}" download="market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv" style="text-decoration: none;">
    <div style="
        background-color: #334155;
        color: #F1F5F9;
        padding: 10px 18px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        width: auto;
        text-align: center;
        transition: background 0.2s;
        border: none;
        cursor: pointer;
    " onmouseover="this.style.background='#475569'" onmouseout="this.style.background='#334155'">
        📥 Verileri CSV Olarak İndir
    </div>
</a>
""", unsafe_allow_html=True)