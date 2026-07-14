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

    col1, col2, col3 = st.columns([1,1,1], gap="medium")

    with col1:
        st.markdown(f"""
        <div style="
            background:#1E293B;
            padding:12px 18px;
            border-radius:12px;
            border-left:5px solid #FFD700;
        ">
            <h5 style="margin:0;">🕒 Son Güncelleme</h5>
            <h3 style="margin-top:10px;">{formatted_time}</h3>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="
            background:#3b1d1d;
            padding:18px;
            border-radius:12px;
            text-align:center;
        ">
        <h5>⬇️ En Düşük</h5>
        <h3>{minimum:.2f} {suffix}</h3>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="
            background:#1c3154;
            padding:18px;
            border-radius:12px;
            text-align:center;
        ">
        <h5 style="margin:0 0 12px 0;">📊 Ortalama</h5>
        <h3 style="margin:0;">{average:.2f} {suffix}</h3>
        </div>
        """, unsafe_allow_html=True)
st.markdown("""
<style>

.block-container{
    padding-top:2rem;
}

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

formatted_time = pd.to_datetime(latest["timestamp"]).strftime("%d.%m.%Y %H:%M:%S")

if latest is None:
    st.warning("Henüz veritabanında veri bulunmuyor.")
    st.stop()

col1, col2 = st.columns([5,1])

with col1:
    st.markdown(f"""
    <div style="
        background:#1E293B;
        padding:18px;
        border-radius:15px;
        border-left:6px solid #FFD700;
    ">
        <h4 style="margin-bottom:5px;">🕒 Son Güncelleme</h4>
        <h2>{formatted_time}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.write("")
    st.write("")
    if st.button("🔄 Yenile"):
        st.cache_data.clear()
        st.rerun()

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
            fig.update_traces(
                line=dict(width=3),
                marker=dict(size=8)
            )
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

            fig.update_traces(
                line=dict(width=3),
                marker=dict(size=8)
            )

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

        # ============================
        # DÖVİZ ANALİZİ
        # ============================

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

            fig.update_traces(
                line=dict(width=3),
                marker=dict(size=8)
            )
            
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

            fig.update_traces(
                line=dict(width=3),
                marker=dict(size=8)
            )
            
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

            fig.update_traces(
                line=dict(width=3),
                marker=dict(size=8)
            )
            
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

# Tablo için en yeni kayıt üstte
df_table = df.sort_values("timestamp", ascending=False)

st.dataframe(
    df_table,
    width="stretch",
)

csv = df_table.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Verileri CSV Olarak İndir",
    data=csv,
    file_name="market_data.csv",
    mime="text/csv",
)