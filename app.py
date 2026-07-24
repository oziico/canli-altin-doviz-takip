import platform
import os

if platform.system() == "Darwin":
    os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st

from database import (
    get_all_market_data,
    get_latest_market_data,
    insert_alert,
    get_active_alerts,
    delete_alert,
    get_alert_history,
    alert_exists,
    get_last_triggered_alert,
)

st.set_page_config(
    page_title="Canlı Altın ve Döviz Takip Sistemi",
    page_icon="📈",
    layout="wide",
)

st.markdown("""
<style>
.block-container{
    padding-top:2rem;
}
.metric-container {
    background-color: #1E293B;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #334155;
}
</style>
""", unsafe_allow_html=True)

from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

st_autorefresh(
    interval=10000,
    key="datarefresh"
)


last_alert = get_last_triggered_alert()

if "last_seen_alert_id" not in st.session_state:

    if last_alert is not None:
        st.session_state.last_seen_alert_id = last_alert["id"]
    else:
        st.session_state.last_seen_alert_id = None

last_alert = get_last_triggered_alert()

alert_name_map = {
    "usd_try": "USD / TRY",
    "eur_try": "EUR / TRY",
    "gbp_try": "GBP / TRY",
    "gold_ounce": "Ons Altın ($)",
    "gold_gram": "Gram Altın (TL)",
}

# --------------------------------------------------
# ALARM TAKİP DURUMU
# --------------------------------------------------

# Uygulama ilk açıldığında mevcut son alarmı başlangıç noktası kabul et.
# Böylece geçmişte tetiklenmiş alarm popup olarak gösterilmez.
if "alert_system_initialized" not in st.session_state:

    st.session_state.alert_system_initialized = True

    st.session_state.last_seen_alert_id = (
        last_alert["id"]
        if last_alert is not None
        else None
    )

    st.session_state.visible_alert_id = None
    st.session_state.last_sound_alert_id = None


# Veritabanında başlangıçtan daha yeni bir alarm oluşmuş mu?
if (
    last_alert is not None
    and last_alert["id"] != st.session_state.last_seen_alert_id
):

    # Yeni alarm bulundu.
    st.session_state.last_seen_alert_id = last_alert["id"]

    # Bu alarmı ekranda göster.
    st.session_state.visible_alert_id = last_alert["id"]


show_alert = (
    last_alert is not None
    and st.session_state.visible_alert_id == last_alert["id"]
)

if show_alert:

    alert_id = last_alert["id"]

    alert_name = alert_name_map.get(
        last_alert["metric"],
        last_alert["metric"]
    )

    if st.session_state.last_sound_alert_id != alert_id:

        components.html(
        """
        <script>
        try {
            const AudioContextClass =
                window.AudioContext || window.webkitAudioContext;

            const audioCtx = new AudioContextClass();

            function beep(startTime, frequency, duration, volume) {
                const oscillator = audioCtx.createOscillator();
                const gainNode = audioCtx.createGain();

                oscillator.connect(gainNode);
                gainNode.connect(audioCtx.destination);

                oscillator.type = "square";
                oscillator.frequency.setValueAtTime(
                    frequency,
                    startTime
                );

                gainNode.gain.setValueAtTime(
                    volume,
                    startTime
                );

                gainNode.gain.exponentialRampToValueAtTime(
                    0.001,
                    startTime + duration
                );

                oscillator.start(startTime);
                oscillator.stop(startTime + duration);
            }

            const now = audioCtx.currentTime;

            beep(now, 1000, 0.18, 0.28);
            beep(now + 0.28, 1200, 0.18, 0.28);
            beep(now + 0.56, 1000, 0.25, 0.32);

        } catch (e) {
            console.log("Alarm sesi çalınamadı:", e);
        }
        </script>
        """,
        height=0,
    )

        st.session_state.last_sound_alert_id = alert_id

    st.markdown(
        """
<style>
.alarm-wrapper {
    border: 1px solid rgba(239, 68, 68, 0.55);
    border-left: 5px solid #ef4444;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 10px;

    background:
        linear-gradient(
            135deg,
            rgba(127, 29, 29, 0.18),
            rgba(17, 24, 39, 0.95)
        );

    box-shadow:
        0 10px 30px rgba(0, 0, 0, 0.30);
}

.alarm-header {
    color: #fca5a5;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 8px;
}

.alarm-asset {
    color: #f8fafc;
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 8px;
}

.alarm-info {
    color: #cbd5e1;
    font-size: 14px;
    line-height: 1.7;
}

.alarm-current {
    color: #ffffff;
    font-weight: 700;
}

.alarm-target {
    color: #fbbf24;
    font-weight: 700;
}
</style>
""",
        unsafe_allow_html=True,
    )


    alert_col, close_col = st.columns(
        [12, 1],
        vertical_alignment="top"
    )

    with alert_col:

        alarm_html = (
            '<div class="alarm-wrapper">'
            '<div class="alarm-header">🚨 Fiyat Alarmı Tetiklendi</div>'
            f'<div class="alarm-asset">{alert_name}</div>'
            '<div class="alarm-info">'
            'Güncel fiyat: '
            f'<span class="alarm-current">{last_alert["current_value"]:.4f}</span>'
            '<br>'
            'Alarm koşulu: '
            f'<span class="alarm-target">{last_alert["condition"]} '
            f'{last_alert["target_value"]:.4f}</span>'
            '</div>'
            '</div>'
        )

        st.markdown(
            alarm_html,
            unsafe_allow_html=True
        )

    with close_col:

        if st.button(
            "✕",
            key=f"dismiss_alert_{alert_id}",
            help="Alarm bildirimini kapat",
            use_container_width=True,
        ):

            st.session_state.visible_alert_id = None

            st.rerun()
                
st.title("📈 Canlı Altın ve Döviz Takip Sistemi")
st.caption("Profesyonel Finansal Analiz ve Takip Paneli (SQLite Live Data)")

latest = get_latest_market_data()
data_all = get_all_market_data()
df_all = pd.DataFrame(data_all)

if latest is None or df_all.empty:
    st.warning("Henüz veritabanında yeterli veri bulunmuyor.")
    st.stop()

df_all["timestamp"] = pd.to_datetime(df_all["timestamp"])
last_time = pd.to_datetime(latest["timestamp"])
formatted_time = last_time.strftime("%d.%m.%Y %H:%M:%S")

metrics = ['usd_try', 'eur_try', 'gbp_try', 'gold_ounce', 'gold_gram']
changes_24h = {}
volatility_24h = {}

t_threshold = last_time - timedelta(days=1)
df_24h = df_all[df_all["timestamp"] >= t_threshold].sort_values("timestamp")

for col in metrics:
    v_now = latest[col]
    
    if not df_24h.empty and len(df_24h) >= 2:
        v_prev = df_24h[col].iloc[0]
        pct = ((v_now - v_prev) / v_prev) * 100 if v_prev > 0 else 0.0
        pct_returns = df_24h[col].pct_change().dropna()
        vol = pct_returns.std() * 100
    else:
        v_prev = v_now
        pct = 0.0
        vol = 0.0
        
    changes_24h[col] = {"diff": v_now - v_prev, "pct": pct}
    volatility_24h[col] = vol

name_map = {
    'usd_try': 'USD / TRY',
    'eur_try': 'EUR / TRY',
    'gbp_try': 'GBP / TRY',
    'gold_ounce': 'Ons Altın ($)',
    'gold_gram': 'Gram Altın (TL)'
}

sorted_changes = sorted(changes_24h.items(), key=lambda x: x[1]["pct"])
max_dropped = sorted_changes[0]
max_gained = sorted_changes[-1]

max_volatile_key = max(volatility_24h, key=volatility_24h.get)
max_volatility_val = volatility_24h[max_volatile_key]

st.sidebar.header("🔔 Fiyat Alarm Sistemi")

alert_metric = st.sidebar.selectbox(
    "Varlık Seçin", 
    options=metrics, 
    format_func=lambda x: name_map[x],
    key="alert_metric_select"
)

current_asset_value = float(latest[alert_metric])
alert_target_str = st.sidebar.text_input(
    "Hedef Fiyat", 
    value=f"{current_asset_value:.4f}",
    key=f"target_input_{alert_metric}"
)

alert_condition = st.sidebar.selectbox(
    "Koşul", 
    options=[">", "<"], 
    format_func=lambda x: "Büyükse (>)" if x == ">" else "Küçükse (<)"
)

if st.sidebar.button("Alarm Kur", use_container_width=True):
    try:
        alert_target = float(alert_target_str)

        is_already_passed = False
        if alert_condition == ">" and current_asset_value > alert_target:
            is_already_passed = True
        elif alert_condition == "<" and current_asset_value < alert_target:
            is_already_passed = True

        if is_already_passed:
            st.sidebar.warning(
                f"⚠️ Mevcut fiyat ({current_asset_value:.4f}) zaten girdiğiniz hedeften "
                f"{'büyük' if alert_condition == '>' else 'küçük'}. Alarm kurulamaz!"
            )
        else:
            if alert_exists(alert_metric, alert_condition, alert_target):
                st.sidebar.warning("⚠️ Bu alarm zaten aktif.")
            else:
                insert_alert(alert_metric, alert_condition, alert_target)
                st.sidebar.success(
                    f"✅ Alarm kuruldu: {name_map[alert_metric]} {alert_condition} {alert_target:.4f}"
                )

    except ValueError:
        st.sidebar.error("Lütfen geçerli bir sayı girin!")

st.sidebar.subheader("📌 Aktif Alarmlarınız")
current_active = get_active_alerts()
if not current_active:
    st.sidebar.info("Bekleyen aktif alarm bulunmuyor.")
else:
    for act in current_active:
        col_lbl, col_btn = st.sidebar.columns([3, 1])
        with col_lbl:
            st.write(f"**{name_map[act['metric']]}** {act['condition']} **{act['target_value']:.2f}**")
        with col_btn:
            if st.button("Sil", key=f"del_{act['id']}"):
                delete_alert(act['id'])

st.sidebar.subheader("📜 Alarm Geçmişi")
history = get_alert_history()

if not history:
    st.sidebar.info("Henüz tetiklenen alarm yok.")
else:
    for item in history[:10]:
        st.sidebar.write(f"🔔 {name_map[item['metric']]}")
        st.sidebar.caption(
            f"{item['current_value']:.4f} {item['condition']} {item['target_value']:.4f}"
        )
        st.sidebar.caption(item["triggered_at"])

top_col1, top_col2, top_col3 = st.columns(3)

with top_col1:
    color = "#4ade80" if max_gained[1]["pct"] >= 0 else "#f87171"
    sign = "▲" if max_gained[1]["pct"] >= 0 else "▼"
    st.markdown(f"""
    <div style="background: #1E293B; padding: 10px; border-radius: 8px; border-left: 4px solid #4ade80; text-align: center;">
        <span style="font-size: 13px; color: #94A3B8;">🏆 En Çok Artan Varlık (24s)</span><br/>
        <strong style="color: #F1F5F9; font-size: 15px;">{name_map[max_gained[0]]}</strong> 
        <span style="color: {color}; font-weight: bold; font-size: 14px;">{sign} %{abs(max_gained[1]["pct"]):.2f}</span>
    </div>
    """, unsafe_allow_html=True)

with top_col2:
    color = "#f87171" if max_dropped[1]["pct"] < 0 else "#4ade80"
    sign = "▼" if max_dropped[1]["pct"] < 0 else "▲"
    st.markdown(f"""
    <div style="background: #1E293B; padding: 10px; border-radius: 8px; border-left: 4px solid #f87171; text-align: center;">
        <span style="font-size: 13px; color: #94A3B8;">📉 En Çok Düşen Varlık (24s)</span><br/>
        <strong style="color: #F1F5F9; font-size: 15px;">{name_map[max_dropped[0]]}</strong> 
        <span style="color: {color}; font-weight: bold; font-size: 14px;">{sign} %{abs(max_dropped[1]["pct"]):.2f}</span>
    </div>
    """, unsafe_allow_html=True)

with top_col3:
    st.markdown(f"""
    <div style="background: #1E293B; padding: 10px; border-radius: 8px; border-left: 4px solid #eab308; text-align: center;">
        <span style="font-size: 13px; color: #94A3B8;">⚡ En Oynak Varlık (24s Risk Lideri)</span><br/>
        <strong style="color: #F1F5F9; font-size: 15px;">{name_map[max_volatile_key]}</strong> 
        <span style="color: #eab308; font-weight: bold; font-size: 14px;">⚡ %{max_volatility_val:.2f}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div style="
    background: #111827;
    padding: 10px 16px;
    border-radius: 8px;
    border: 1px solid #1F2937;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    margin-top: 15px;
    margin-bottom: 25px;
">
    <div style="display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 13px; color: #9BD; margin: 0;">🕒 Son Veri Girişi:</span>
        <strong style="font-size: 13px; color: #F1F5F9; margin: 0;">{formatted_time}</strong>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("💵 Döviz Kurları")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(
            label="USD / TRY (24s)", 
            value=f"{latest['usd_try']:.4f}", 
            delta=f"{changes_24h['usd_try']['pct']:.2f}%"
        )
        st.caption(f"⚡ Volatilite: %{volatility_24h['usd_try']:.2f}")
    with c2:
        st.metric(
            label="EUR / TRY (24s)", 
            value=f"{latest['eur_try']:.4f}", 
            delta=f"{changes_24h['eur_try']['pct']:.2f}%"
        )
        st.caption(f"⚡ Volatilite: %{volatility_24h['eur_try']:.2f}")
    with c3:
        st.metric(
            label="GBP / TRY (24s)", 
            value=f"{latest['gbp_try']:.4f}", 
            delta=f"{changes_24h['gbp_try']['pct']:.2f}%"
        )
        st.caption(f"⚡ Volatilite: %{volatility_24h['gbp_try']:.2f}")

with col2:
    st.subheader("🥇 Altın Fiyatları")
    c1, c2 = st.columns(2)
    with c1:
        st.metric(
            label="Gram Altın (TL) (24s)", 
            value=f"{latest['gold_gram']:.2f}", 
            delta=f"{changes_24h['gold_gram']['pct']:.2f}%"
        )
        st.caption(f"⚡ Volatilite: %{volatility_24h['gold_gram']:.2f}")
    with c2:
        st.metric(
            label="Ons Altın ($) (24s)", 
            value=f"{latest['gold_ounce']:.2f}", 
            delta=f"{changes_24h['gold_ounce']['pct']:.2f}%"
        )
        st.caption(f"⚡ Volatilite: %{volatility_24h['gold_ounce']:.2f}")

st.divider()

def show_statistics(df, column, suffix):
    maximum = df[column].max()
    minimum = df[column].min()
    average = df[column].mean()

    col1, col2, col3 = st.columns(3, gap="small")
    precision = ".4f" if column in ['usd_try', 'eur_try', 'gbp_try'] else ".2f"
    
    val_max = f"{maximum:{precision}} {suffix}"
    val_min = f"{minimum:{precision}} {suffix}"
    val_avg = f"{average:{precision}} {suffix}"

    card_style = (
        "display: flex; "
        "flex-direction: column; "
        "justify-content: space-evenly; "
        "align-items: center; "
        "height: 90px; "
        "border-radius: 8px; "
        "padding: 10px; "
        "text-align: center; "
        "box-sizing: border-box;"
    )

    with col1:
        st.markdown(f"""
        <div style="{card_style} background: #1e352f;">
            <h5 style="margin: 0; color: #4ade80; font-size: 12px; font-weight: 600;">📈 En Yüksek</h5>
            <h3 style="margin: 0; font-size: 15px; font-weight: bold; color: #f1f5f9;">{val_max}</h3>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="{card_style} background: #3b1d1d;">
            <h5 style="margin: 0; color: #f87171; font-size: 12px; font-weight: 600;">⬇️ En Düşük</h5>
            <h3 style="margin: 0; font-size: 15px; font-weight: bold; color: #f1f5f9;">{val_min}</h3>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="{card_style} background: #1c3154;">
            <h5 style="margin: 0; color: #60a5fa; font-size: 12px; font-weight: 600;">📊 Ortalama</h5>
            <h3 style="margin: 0; font-size: 15px; font-weight: bold; color: #f1f5f9;">{val_avg}</h3>
        </div>
        """, unsafe_allow_html=True)

df = df_all.copy()

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
                height:600px;
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
        if not df.empty:
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
        
        if not df.empty:
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
                height:600px;
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
                height:600px;
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
            margin=dict(l=10, r=10, t=40, b=10),
        )
        if not df.empty:
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
            margin=dict(l=10, r=10, t=40, b=10),
        )
        if not df.empty:
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
            margin=dict(l=10, r=10, t=40, b=10),
        )
        if not df.empty:
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

temp_df = df_table.copy()
if 'timestamp' in temp_df.columns:
    temp_df['timestamp'] = temp_df['timestamp'].astype(str)

csv_data = temp_df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="📥 Verileri CSV Olarak İndir",
    data=csv_data,
    file_name=f"market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv",
    use_container_width=False,
)