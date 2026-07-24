import platform
import os

if platform.system() == "Darwin":
    os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
from analytics import (
    calculate_24h_analysis,
    get_market_leaders,
    add_time_based_moving_averages,
    calculate_time_based_trend,
)

from database import (
    get_all_market_data,
    get_latest_market_data,
    insert_alert,
    get_active_alerts,
    delete_alert,
    get_alert_history,
    alert_exists,
)

from alerts import (
    ALERT_NAME_MAP,
    get_new_alert,
    should_show_alert,
    dismiss_alert,
    should_play_alarm_sound,
    mark_alarm_sound_as_played,
)

st.set_page_config(
    page_title="Canlı Altın ve Döviz Takip Sistemi",
    page_icon="📈",
    layout="wide",
)

st.markdown(
    """
<style>

/* =========================================================
   GLOBAL DESIGN SYSTEM
   ========================================================= */

:root {
    --bg-main: #090D15;
    --surface-1: #101722;
    --surface-2: #151D2B;
    --surface-3: #1A2433;

    --border-soft: rgba(255,255,255,0.07);
    --border-medium: rgba(255,255,255,0.12);

    --text-main: #F8FAFC;
    --text-secondary: #A8B3C7;
    --text-muted: #64748B;

    --positive: #34D399;
    --negative: #FB7185;

    --usd: #22D3EE;
    --eur: #60A5FA;
    --gbp: #A78BFA;
    --gram: #FACC15;
    --ounce: #FB923C;
}


/* =========================================================
   STREAMLIT BASE
   ========================================================= */

.stApp {
    background:
        radial-gradient(
            circle at 8% 5%,
            rgba(124, 58, 237, 0.14),
            transparent 28%
        ),
        radial-gradient(
            circle at 90% 18%,
            rgba(6, 182, 212, 0.10),
            transparent 30%
        ),
        radial-gradient(
            circle at 55% 75%,
            rgba(236, 72, 153, 0.055),
            transparent 32%
        ),
        linear-gradient(
            145deg,
            #080B14 0%,
            #0E1020 38%,
            #101426 68%,
            #080D17 100%
        );
}

.block-container {
    padding-top: 2rem;
    max-width: 1500px;
}


/* =========================================================
   PREMIUM HERO
   ========================================================= */

.hero-card {

    position: relative;
    overflow: hidden;

    padding: 24px 28px;

    margin-bottom: 18px;

    border-radius: 20px;

    border: 1px solid rgba(255,255,255,0.09);

    background:
        linear-gradient(
            120deg,
            rgba(20,29,43,0.97),
            rgba(12,18,30,0.98)
        );

    box-shadow:
        0 25px 70px rgba(0,0,0,0.35),
        inset 0 1px 0 rgba(255,255,255,0.05);
}


.hero-card::before {

    content: "";

    position: absolute;

    width: 360px;
    height: 360px;

    right: -100px;
    top: -180px;

    background:
        radial-gradient(
            circle,
            rgba(59,130,246,0.18),
            transparent 67%
        );

    pointer-events: none;
}


.hero-card::after {

    content: "";

    position: absolute;

    width: 280px;
    height: 280px;

    right: 120px;
    bottom: -230px;

    background:
        radial-gradient(
            circle,
            rgba(168,85,247,0.12),
            transparent 70%
        );

    pointer-events: none;
}


.hero-top {

    position: relative;
    z-index: 2;

    display: flex;
    justify-content: space-between;
    align-items: flex-start;

    gap: 24px;
}


.hero-eyebrow {

    display: inline-flex;

    margin-bottom: 12px;

    color: #7DD3FC;

    font-size: 11px;
    font-weight: 800;

    letter-spacing: 2px;
    text-transform: uppercase;
}


.hero-title {

    max-width: 800px;

    color: #F8FAFC;

    font-size: clamp(25px, 2.4vw, 34px);

    font-weight: 800;

    line-height: 1.15;

    letter-spacing: -0.8px;
}


.hero-subtitle {

    max-width: 700px;

    margin-top: 9px;

    color: #94A3B8;

    font-size: 13px;
    line-height: 1.6;
}


.live-pill {

    flex-shrink: 0;

    display: inline-flex;
    align-items: center;

    gap: 9px;

    padding: 9px 14px;

    border-radius: 999px;

    border: 1px solid rgba(52,211,153,0.25);

    background:
        linear-gradient(
            180deg,
            rgba(52,211,153,0.10),
            rgba(52,211,153,0.04)
        );

    color: #6EE7B7;

    font-size: 11px;
    font-weight: 800;

    letter-spacing: 1.2px;
}


.live-dot {

    display: inline-block;

    width: 7px;
    height: 7px;

    border-radius: 50%;

    background: #34D399;

    box-shadow:
        0 0 0 4px rgba(52,211,153,0.10),
        0 0 14px rgba(52,211,153,0.55);
}


/* =========================================================
   SECTION HEADER
   ========================================================= */

.section-kicker {

    margin-top: 8px;
    margin-bottom: 12px;

    color: #64748B;

    font-size: 11px;
    font-weight: 800;

    letter-spacing: 1.5px;
    text-transform: uppercase;
}


/* =========================================================
   MARKET CARDS
   ========================================================= */

.market-card {

    position: relative;
    overflow: hidden;

    min-height: 154px;

    padding: 20px;

    border-radius: 19px;

    border: 1px solid var(--border-soft);

    background:
        linear-gradient(
            145deg,
            rgba(21,29,43,0.96),
            rgba(12,18,29,0.98)
        );

    box-shadow:
        0 12px 28px rgba(0,0,0,0.20),
        inset 0 1px 0 rgba(255,255,255,0.035);

    transition:
        transform .20s ease,
        border-color .20s ease,
        box-shadow .20s ease;
}


.market-card:hover {

    transform: translateY(-4px);

    border-color: rgba(255,255,255,0.15);

    box-shadow:
        0 20px 42px rgba(0,0,0,0.30),
        inset 0 1px 0 rgba(255,255,255,0.05);
}


.market-card::before {

    content: "";

    position: absolute;

    top: 0;
    left: 0;

    width: 100%;
    height: 3px;

    background: var(--asset-color);
}


.market-card::after {

    content: "";

    position: absolute;

    width: 130px;
    height: 130px;

    right: -65px;
    top: -65px;

    border-radius: 50%;

    background: var(--asset-glow);

    filter: blur(4px);

    pointer-events: none;
}


.asset-top {

    position: relative;
    z-index: 2;

    display: flex;

    align-items: center;
    justify-content: space-between;
}


.asset-symbol {

    width: 38px;
    height: 38px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 11px;

    background: var(--asset-soft);

    color: var(--asset-color);

    font-size: 15px;
    font-weight: 900;
}


.asset-label {

    color: #94A3B8;

    font-size: 11px;
    font-weight: 800;

    letter-spacing: 0.7px;
}


.asset-value {

    position: relative;
    z-index: 2;

    margin-top: 18px;

    color: #F8FAFC;

    font-size: 26px;
    font-weight: 800;

    letter-spacing: -0.7px;
}


.asset-footer {

    position: relative;
    z-index: 2;

    margin-top: 16px;

    display: flex;
    justify-content: space-between;

    align-items: center;

    gap: 8px;
}


.change-positive,
.change-negative {

    display: inline-flex;

    align-items: center;

    padding: 5px 8px;

    border-radius: 8px;

    font-size: 11px;
    font-weight: 800;
}


.change-positive {

    color: #6EE7B7;

    background: rgba(52,211,153,0.09);
}


.change-negative {

    color: #FDA4AF;

    background: rgba(251,113,133,0.09);
}


.asset-volatility {

    color: #64748B;

    font-size: 10px;
    font-weight: 700;

    letter-spacing: 0.3px;
}


/* ASSET THEMES */

.asset-usd {
    --asset-color: #22D3EE;
    --asset-soft: rgba(34,211,238,0.10);
    --asset-glow: rgba(34,211,238,0.12);
}

.asset-eur {
    --asset-color: #60A5FA;
    --asset-soft: rgba(96,165,250,0.10);
    --asset-glow: rgba(96,165,250,0.12);
}

.asset-gbp {
    --asset-color: #A78BFA;
    --asset-soft: rgba(167,139,250,0.10);
    --asset-glow: rgba(167,139,250,0.12);
}

.asset-gram {
    --asset-color: #FACC15;
    --asset-soft: rgba(250,204,21,0.10);
    --asset-glow: rgba(250,204,21,0.14);
}

.asset-ounce {
    --asset-color: #FB923C;
    --asset-soft: rgba(251,146,60,0.10);
    --asset-glow: rgba(251,146,60,0.13);
}


/* =========================================================
   MARKET INSIGHT CARDS
   ========================================================= */

.insight-card {

    min-height: 110px;

    padding: 17px 18px;

    border-radius: 16px;

    border: 1px solid rgba(255,255,255,0.07);

    background:
        linear-gradient(
            145deg,
            rgba(17,24,39,0.92),
            rgba(11,17,28,0.96)
        );

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.025);
}


.insight-label {

    color: #64748B;

    font-size: 10px;
    font-weight: 800;

    letter-spacing: 1px;
    text-transform: uppercase;
}


.insight-value {

    margin-top: 10px;

    color: #F1F5F9;

    font-size: 16px;
    font-weight: 750;
}


.insight-positive {

    margin-top: 6px;

    color: #34D399;

    font-size: 12px;
    font-weight: 700;
}


.insight-negative {

    margin-top: 6px;

    color: #FB7185;

    font-size: 12px;
    font-weight: 700;
}


.insight-neutral {

    margin-top: 6px;

    color: #94A3B8;

    font-size: 12px;
    font-weight: 700;
}

/* =========================================================
   PREMIUM SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #0C121D 0%,
            #080D15 100%
        );

    border-right:
        1px solid rgba(255,255,255,0.06);
}


section[data-testid="stSidebar"] > div {
    padding-top: 18px;
}


section[data-testid="stSidebar"]
div[data-baseweb="select"] > div {

    background:
        rgba(255,255,255,0.035);

    border-color:
        rgba(255,255,255,0.08);

    border-radius: 11px;
}


section[data-testid="stSidebar"]
input {

    background:
        rgba(255,255,255,0.035);

    border:
        1px solid rgba(255,255,255,0.08);

    border-radius: 11px;
}


section[data-testid="stSidebar"]
button[kind="primary"] {

    border: none;

    border-radius: 11px;

    min-height: 43px;

    font-weight: 750;

    background:
        linear-gradient(
            135deg,
            #4F46E5,
            #7C3AED
        );

    box-shadow:
        0 8px 22px
        rgba(79,70,229,0.22);

    transition:
        transform .18s ease,
        box-shadow .18s ease;
}


section[data-testid="stSidebar"]
button[kind="primary"]:hover {

    transform: translateY(-1px);

    box-shadow:
        0 12px 30px
        rgba(79,70,229,0.34);
}

/* =========================================================
   MOBILE
   ========================================================= */

@media (max-width: 850px) {

    .hero-top {
        flex-direction: column;
    }

    .hero-title {
        font-size: 30px;
    }

}
/* =========================================================
   PREMIUM CHART PANELS
   ========================================================= */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background:
        linear-gradient(
            145deg,
            rgba(17, 24, 39, 0.88),
            rgba(9, 13, 21, 0.96)
        );

    border: 1px solid rgba(255, 255, 255, 0.075) !important;
    border-radius: 20px !important;

    box-shadow:
        0 16px 45px rgba(0, 0, 0, 0.18),
        inset 0 1px 0 rgba(255, 255, 255, 0.025);

    padding: 14px 16px 20px 16px;

    transition:
        border-color 0.2s ease,
        box-shadow 0.2s ease;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(255, 255, 255, 0.12) !important;

    box-shadow:
        0 20px 55px rgba(0, 0, 0, 0.24),
        inset 0 1px 0 rgba(255, 255, 255, 0.035);
}

</style>
""",
    unsafe_allow_html=True,
)

from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

st_autorefresh(
    interval=10000,
    key="datarefresh"
)


last_alert = get_new_alert()

show_alert = should_show_alert(last_alert)

if show_alert:

    alert_id = last_alert["id"]

    alert_name = ALERT_NAME_MAP.get(
        last_alert["metric"],
        last_alert["metric"]
    )

    if should_play_alarm_sound(alert_id):

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

        mark_alarm_sound_as_played(alert_id)

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

            dismiss_alert()
            st.rerun()
                
header_html = (
    '<div class="hero-card">'
    '<div class="hero-top">'
    '<div>'
    '<div class="hero-eyebrow">FİNANSAL PİYASA TAKİP PANELİ</div>'
    '<div class="hero-title">'
    'Canlı Altın ve Döviz Takip Sistemi'
    '</div>'
    '<div class="hero-subtitle">'
    'Gerçek zamanlı döviz ve altın fiyatlarını izleyin, '
    'piyasa hareketlerini analiz edin ve belirlediğiniz '
    'fiyat seviyeleri için anlık alarm oluşturun.'
    '</div>'
    '</div>'
    '<div class="live-pill">'
    '<span class="live-dot"></span>'
    '<span>CANLI PİYASA</span>'
    '</div>'
    '</div>'
    '</div>'
)

st.markdown(
    header_html,
    unsafe_allow_html=True,
)

latest = get_latest_market_data()
data_all = get_all_market_data()
df_all = pd.DataFrame(data_all)

if latest is None or df_all.empty:
    st.warning("Henüz veritabanında yeterli veri bulunmuyor.")
    st.stop()

df_all["timestamp"] = pd.to_datetime(df_all["timestamp"])
last_time = pd.to_datetime(latest["timestamp"])
formatted_time = last_time.strftime("%d.%m.%Y %H:%M:%S")

st.markdown(f"""
<div style="
    background: rgba(148, 163, 184, 0.08);
    padding: 10px 16px;
    border-radius: 8px;
    border: 1px solid rgba(148, 163, 184, 0.14);
    display: flex;
    justify-content: flex-start;
    align-items: center;
    margin-top: 4px;
    margin-bottom: 18px;
">
    <div style="display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 13px; color: #9BD; margin: 0;">🕒 Son Veri Girişi:</span>
        <strong style="font-size: 13px; color: #F1F5F9; margin: 0;">{formatted_time}</strong>
    </div>
</div>
""", unsafe_allow_html=True)

metrics = [
    "usd_try",
    "eur_try",
    "gbp_try",
    "gold_ounce",
    "gold_gram",
]

changes_24h, volatility_24h = calculate_24h_analysis(
    df_all,
    latest,
    metrics,
)

(
    max_dropped,
    max_gained,
    max_volatile_key,
    max_volatility_val,
) = get_market_leaders(
    changes_24h,
    volatility_24h,
)

name_map = {
    'usd_try': 'USD / TRY',
    'eur_try': 'EUR / TRY',
    'gbp_try': 'GBP / TRY',
    'gold_ounce': 'Ons Altın ($)',
    'gold_gram': 'Gram Altın (TL)'
}
# =========================================================
# SIDEBAR - PRICE ALERT CENTER
# =========================================================

sidebar_header_html = (
    '<div style="padding:6px 2px 18px 2px;">'

    '<div style="'
    'color:#64748B;'
    'font-size:10px;'
    'font-weight:800;'
    'letter-spacing:1.6px;'
    'margin-bottom:6px;'
    '">'
    'ALARM MERKEZİ'
    '</div>'

    '<div style="'
    'color:#F8FAFC;'
    'font-size:22px;'
    'font-weight:800;'
    'letter-spacing:-0.4px;'
    '">'
    'Fiyat Alarmı'
    '</div>'

    '<div style="'
    'color:#94A3B8;'
    'font-size:12px;'
    'line-height:1.6;'
    'margin-top:6px;'
    '">'
    'Kritik fiyat seviyelerini belirleyin ve piyasa hedefinize '
    'ulaştığında anında bildirim alın.'
    '</div>'

    '</div>'
)

st.sidebar.markdown(
    sidebar_header_html,
    unsafe_allow_html=True,
)
# ---------------------------------------------------------
# VARLIK SEÇİMİ
# ---------------------------------------------------------

alert_metric = st.sidebar.selectbox(
    "Varlık",
    options=metrics,
    format_func=lambda x: name_map[x],
    key="alert_metric_select",
)

current_asset_value = float(
    latest[alert_metric]
)


# Mevcut fiyat bilgi kartı
st.sidebar.markdown(
    (
        '<div style="'
        'margin:4px 0 14px 0;'
        'padding:13px 14px;'
        'border-radius:13px;'
        'border:1px solid rgba(255,255,255,0.07);'
        'background:linear-gradient('
        '135deg,'
        'rgba(30,41,59,0.75),'
        'rgba(15,23,42,0.90)'
        ');'
        '">'
        '<div style="'
        'color:#64748B;'
        'font-size:9px;'
        'font-weight:800;'
        'letter-spacing:1px;'
        '">'
        'MEVCUT PİYASA FİYATI'
        '</div>'
        '<div style="'
        'margin-top:6px;'
        'color:#F8FAFC;'
        'font-size:22px;'
        'font-weight:800;'
        '">'
        f'{current_asset_value:.4f}'
        '</div>'
        '<div style="'
        'margin-top:3px;'
        'color:#94A3B8;'
        'font-size:11px;'
        '">'
        f'{name_map[alert_metric]}'
        '</div>'
        '</div>'
    ),
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# ALARM FORMU
# ---------------------------------------------------------

alert_target_str = st.sidebar.text_input(
    "Hedef Fiyat",
    value=f"{current_asset_value:.4f}",
    key=f"target_input_{alert_metric}",
)

alert_condition = st.sidebar.selectbox(
    "Alarm Koşulu",
    options=[">", "<"],
    format_func=lambda x: (
        "Fiyat hedefin üzerine çıkarsa"
        if x == ">"
        else "Fiyat hedefin altına düşerse"
    ),
)

if st.sidebar.button(
    "Alarm Oluştur",
    use_container_width=True,
    type="primary",
):

    try:

        alert_target = float(
            alert_target_str
        )

        is_already_passed = False

        if (
            alert_condition == ">"
            and current_asset_value > alert_target
        ):
            is_already_passed = True

        elif (
            alert_condition == "<"
            and current_asset_value < alert_target
        ):
            is_already_passed = True


        if is_already_passed:

            direction_text = (
                "üzerinde"
                if alert_condition == ">"
                else "altında"
            )

            st.sidebar.warning(
                f"Mevcut fiyat zaten belirlediğiniz "
                f"hedef değerin {direction_text}. "
                f"Lütfen farklı bir hedef belirleyin."
            )

        elif alert_exists(
            alert_metric,
            alert_condition,
            alert_target,
        ):

            st.sidebar.warning(
                "Bu kriterlere sahip aktif bir alarm zaten mevcut."
            )

        else:

            insert_alert(
                alert_metric,
                alert_condition,
                alert_target,
            )

            st.sidebar.success(
                f"Alarm oluşturuldu · "
                f"{name_map[alert_metric]} "
                f"{alert_condition} "
                f"{alert_target:.4f}"
            )

    except ValueError:

        st.sidebar.error(
            "Lütfen geçerli bir hedef fiyat girin."
        )


# =====================================================
# ACTIVE ALERTS
# =====================================================

st.sidebar.markdown(
    (
        '<div style="margin-top:24px;margin-bottom:10px;">'
        '<div style="color:#64748B;font-size:10px;font-weight:800;'
        'letter-spacing:1.5px;">AKTİF ALARMLAR</div>'
        '<div style="color:#F8FAFC;font-size:16px;font-weight:800;'
        'margin-top:4px;">Bekleyen Alarmlar</div>'
        '</div>'
    ),
    unsafe_allow_html=True,
)

current_active = get_active_alerts()

if not current_active:

    st.sidebar.markdown(
        '<div style="'
        'padding:14px 15px;'
        'border-radius:14px;'
        'border:1px solid rgba(255,255,255,0.06);'
        'background:rgba(15,23,42,0.45);'
        'color:#64748B;'
        'font-size:12px;'
        'line-height:1.5;'
        '">'
        '◌ Bekleyen aktif alarm bulunmuyor.'
        '</div>',
        unsafe_allow_html=True,
    )

else:

    for act in current_active:

        asset_name = name_map[act["metric"]]

        condition_text = (
            "Üzerine çıkarsa"
            if act["condition"] == ">"
            else "Altına düşerse"
        )

        alert_col, delete_col = st.sidebar.columns(
            [4, 1],
            vertical_alignment="center",
        )

        with alert_col:

            active_alert_html = (
                '<div style="'
                'padding:12px 13px;'
                'border-radius:13px;'
                'border:1px solid rgba(255,255,255,0.06);'
                'background:rgba(15,23,42,0.55);'
                '">'
                '<div style="'
                'color:#F8FAFC;'
                'font-size:12px;'
                'font-weight:800;'
                '">'
                f'{asset_name}'
                '</div>'
                '<div style="'
                'margin-top:5px;'
                'color:#94A3B8;'
                'font-size:10px;'
                '">'
                f'{condition_text} · '
                f'{act["target_value"]:.4f}'
                '</div>'
                '</div>'
            )

            st.markdown(
                active_alert_html,
                unsafe_allow_html=True,
            )

        with delete_col:

            if st.button(
                "✕",
                key=f"del_{act['id']}",
                help="Alarmı sil",
                use_container_width=True,
            ):
                delete_alert(act["id"])
                st.rerun()


# =====================================================
# ALERT HISTORY
# =====================================================

st.sidebar.markdown(
    '<div style="margin-top:26px;margin-bottom:10px;">'
    '<div style="color:#64748B;font-size:10px;font-weight:800;'
    'letter-spacing:1.5px;">ALARM GEÇMİŞİ</div>'
    '<div style="color:#F8FAFC;font-size:16px;font-weight:800;'
    'margin-top:4px;">Alarm Geçmişi</div>'
    '</div>',
    unsafe_allow_html=True,
)

history = get_alert_history()

if not history:

    st.sidebar.markdown(
        '<div style="'
        'padding:14px 15px;'
        'border-radius:14px;'
        'border:1px solid rgba(255,255,255,0.06);'
        'background:rgba(15,23,42,0.45);'
        'color:#64748B;'
        'font-size:12px;'
        '">'
        'Henüz tetiklenen alarm bulunmuyor.'
        '</div>',
        unsafe_allow_html=True,
    )

else:

    for item in history[:5]:

        asset_name = name_map[item["metric"]]

        history_html = (
            '<div style="'
            'padding:11px 13px;'
            'margin-bottom:7px;'
            'border-left:2px solid rgba(96,165,250,0.55);'
            'background:rgba(15,23,42,0.30);'
            '">'
            '<div style="'
            'color:#CBD5E1;'
            'font-size:11px;'
            'font-weight:700;'
            '">'
            f'{asset_name}'
            '</div>'
            '<div style="'
            'margin-top:4px;'
            'color:#64748B;'
            'font-size:9px;'
            '">'
            f'{item["current_value"]:.4f} '
            f'{item["condition"]} '
            f'{item["target_value"]:.4f}'
            '</div>'
            '<div style="'
            'margin-top:3px;'
            'color:#475569;'
            'font-size:9px;'
            '">'
            f'{item["triggered_at"]}'
            '</div>'
            '</div>'
        )

        st.sidebar.markdown(
            history_html,
            unsafe_allow_html=True,
        )

        
st.markdown(
    '<div class="section-kicker">PİYASA ÖZETİ</div>',
    unsafe_allow_html=True,
)

positive_count = sum(
    1
    for item in changes_24h.values()
    if item["pct"] > 0
)

if positive_count >= 4:
    market_mood = "Pozitif"
    mood_class = "insight-positive"
    mood_text = "Alım yönlü momentum"

elif positive_count <= 1:
    market_mood = "Negatif"
    mood_class = "insight-negative"
    mood_text = "Satış baskısı güçlü"

else:
    market_mood = "Dengeli"
    mood_class = "insight-neutral"
    mood_text = "Karışık piyasa görünümü"


insight_cols = st.columns(
    4,
    gap="medium",
)


with insight_cols[0]:

    st.markdown(
        (
            '<div class="insight-card">'
            '<div class="insight-label">En Güçlü Varlık</div>'
            f'<div class="insight-value">{name_map[max_gained[0]]}</div>'
            f'<div class="insight-positive">↗ {max_gained[1]["pct"]:.2f}%</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


with insight_cols[1]:

    loser_pct = max_dropped[1]["pct"]

    loser_class = (
        "insight-negative"
        if loser_pct < 0
        else "insight-positive"
    )

    st.markdown(
        (
            '<div class="insight-card">'
            '<div class="insight-label">En Zayıf Varlık</div>'
            f'<div class="insight-value">{name_map[max_dropped[0]]}</div>'
            f'<div class="{loser_class}">{loser_pct:.2f}%</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


with insight_cols[2]:

    st.markdown(
        (
            '<div class="insight-card">'
            '<div class="insight-label">Volatilite Lideri</div>'
            f'<div class="insight-value">{name_map[max_volatile_key]}</div>'
            f'<div class="insight-neutral">⚡ {max_volatility_val:.2f}% volatilite</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


with insight_cols[3]:

    st.markdown(
        (
            '<div class="insight-card">'
            '<div class="insight-label">Piyasa Görünümü</div>'
            f'<div class="insight-value">{market_mood}</div>'
            f'<div class="{mood_class}">{mood_text}</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="section-kicker" style="margin-top:26px;">'
    'CANLI PİYASA FİYATLARI'
    '</div>',
    unsafe_allow_html=True,
)

market_cols = st.columns(
    5,
    gap="medium",
)

market_cards = [
    {
        "column": "usd_try",
        "label": "ABD DOLARI",
        "symbol": "$",
        "value": f"{latest['usd_try']:.4f}",
        "class": "asset-usd",
        "currency": "TRY",
    },
    {
        "column": "eur_try",
        "label": "EURO",
        "symbol": "€",
        "value": f"{latest['eur_try']:.4f}",
        "class": "asset-eur",
        "currency": "TRY",
    },
    {
        "column": "gbp_try",
        "label": "İNGİLİZ STERLİNİ",
        "symbol": "£",
        "value": f"{latest['gbp_try']:.4f}",
        "class": "asset-gbp",
        "currency": "TRY",
    },
    {
        "column": "gold_gram",
        "label": "GRAM ALTIN",
        "symbol": "Au",
        "value": f"{latest['gold_gram']:.2f}",
        "class": "asset-gram",
        "currency": "TRY",
    },
    {
        "column": "gold_ounce",
        "label": "ONS ALTIN",
        "symbol": "Oz",
        "value": f"{latest['gold_ounce']:.2f}",
        "class": "asset-ounce",
        "currency": "USD",
    },
]


for column_container, card in zip(
    market_cols,
    market_cards,
):

    metric = card["column"]

    change = changes_24h[metric]["pct"]
    volatility = volatility_24h[metric]

    if change >= 0:

        change_class = "change-positive"
        change_icon = "↗"

    else:

        change_class = "change-negative"
        change_icon = "↘"


    card_html = (
        f'<div class="market-card {card["class"]}">'

        '<div class="asset-top">'

        f'<div class="asset-symbol">'
        f'{card["symbol"]}'
        '</div>'

        f'<div class="asset-label">'
        f'{card["label"]}'
        '</div>'

        '</div>'

        f'<div class="asset-value">'
        f'{card["value"]} '

        '<span style="'
        'font-size:11px;'
        'color:#64748B;'
        'font-weight:700;'
        '">'
        f'{card["currency"]}'
        '</span>'

        '</div>'

        '<div class="asset-footer">'

        f'<span class="{change_class}">'
        f'{change_icon} {abs(change):.2f}%'
        '</span>'

        f'<span class="asset-volatility">'
        f'VOL {volatility:.2f}%'
        '</span>'

        '</div>'

        '</div>'
    )

    with column_container:
        st.markdown(
            card_html,
            unsafe_allow_html=True,
        )

def show_statistics(df, column, suffix):
    maximum = df[column].max()
    minimum = df[column].min()
    average = df[column].mean()

    precision = (
        ".4f"
        if column in ["usd_try", "eur_try", "gbp_try"]
        else ".2f"
    )

    val_max = f"{maximum:{precision}} {suffix}"
    val_min = f"{minimum:{precision}} {suffix}"
    val_avg = f"{average:{precision}} {suffix}"

    stats_cols = st.columns(3, gap="small")

    stat_cards = [
        {
            "label": "EN YÜKSEK",
            "value": val_max,
            "accent": "#34D399",
            "soft": "rgba(52,211,153,0.08)",
        },
        {
            "label": "EN DÜŞÜK",
            "value": val_min,
            "accent": "#FB7185",
            "soft": "rgba(251,113,133,0.08)",
        },
        {
            "label": "ORTALAMA",
            "value": val_avg,
            "accent": "#60A5FA",
            "soft": "rgba(96,165,250,0.08)",
        },
    ]

    for container, card in zip(
        stats_cols,
        stat_cards,
    ):
        card_html = (
            '<div style="'
            'padding:14px 15px;'
            'border-radius:14px;'
            'border:1px solid rgba(255,255,255,0.06);'
            f'background:{card["soft"]};'
            'min-height:82px;'
            'display:flex;'
            'flex-direction:column;'
            'justify-content:center;'
            '">'
            f'<div style="'
            f'color:{card["accent"]};'
            'font-size:10px;'
            'font-weight:800;'
            'letter-spacing:1px;'
            '">'
            f'{card["label"]}'
            '</div>'
            '<div style="'
            'margin-top:7px;'
            'color:#F8FAFC;'
            'font-size:15px;'
            'font-weight:800;'
            '">'
            f'{card["value"]}'
            '</div>'
            '</div>'
        )

        with container:
            st.markdown(
                card_html,
                unsafe_allow_html=True,
            )


def show_market_chart(
    df,
    column,
    title,
    suffix,
    line_color,
    precision=4,
):
    analyzed_df = add_time_based_moving_averages(
        df,
        column,
        short_minutes=30,
        long_minutes=60,
    )

    short_ma_column = f"{column}_ma_short"
    long_ma_column = f"{column}_ma_long"

    trend = calculate_time_based_trend(
        df,
        column,
        short_minutes=30,
        long_minutes=60,
    )

    if trend == "Yükseliş Eğilimi":
        trend_text = "YÜKSELİŞ"
        trend_icon = "↗"
        trend_color = "#34D399"
        trend_bg = "rgba(52,211,153,0.09)"

    elif trend == "Düşüş Eğilimi":
        trend_text = "DÜŞÜŞ"
        trend_icon = "↘"
        trend_color = "#FB7185"
        trend_bg = "rgba(251,113,133,0.09)"

    elif trend == "Yetersiz Veri":
        trend_text = "VERİ BİRİKİYOR"
        trend_icon = "◌"
        trend_color = "#FBBF24"
        trend_bg = "rgba(251,191,36,0.08)"

    else:
        trend_text = "YATAY"
        trend_icon = "→"
        trend_color = "#94A3B8"
        trend_bg = "rgba(148,163,184,0.08)"

    chart_header = (
        '<div style="'
        'display:flex;'
        'justify-content:space-between;'
        'align-items:center;'
        'margin-bottom:10px;'
        '">'
        '<div>'
        '<div style="'
        'font-size:18px;'
        'font-weight:800;'
        'color:#F8FAFC;'
        '">'
        f'{title}'
        '</div>'
        '<div style="'
        'margin-top:4px;'
        'font-size:11px;'
        'color:#64748B;'
        '">'
        'Fiyat hareketi ve zaman bazlı trend analizi'
        '</div>'
        '</div>'
        '<div style="'
        f'color:{trend_color};'
        f'background:{trend_bg};'
        f'border:1px solid {trend_color}33;'
        'padding:6px 10px;'
        'border-radius:999px;'
        'font-size:10px;'
        'font-weight:800;'
        'letter-spacing:.6px;'
        '">'
        f'{trend_icon} {trend_text}'
        '</div>'
        '</div>'
    )

    st.markdown(
        chart_header,
        unsafe_allow_html=True,
    )

    fig = px.line(
        analyzed_df,
        x="timestamp",
        y=column,
    )

    fig.update_traces(
        mode="lines",
        line=dict(
            width=2.8,
            color=line_color,
        ),
        name="Fiyat",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "%{x|%d.%m %H:%M}"
            "<extra></extra>"
        ),
    )

    fig.add_scatter(
        x=analyzed_df["timestamp"],
        y=analyzed_df[short_ma_column],
        mode="lines",
        name="30 dk Ortalama",
        line=dict(
            width=1.8,
            dash="dash",
            color="rgba(148,163,184,0.85)",
        ),
        hovertemplate=(
            "30 dk Ortalama: %{y}<br>"
            "%{x|%d.%m %H:%M}"
            "<extra></extra>"
        ),
    )

    fig.add_scatter(
        x=analyzed_df["timestamp"],
        y=analyzed_df[long_ma_column],
        mode="lines",
        name="60 dk Ortalama",
        line=dict(
            width=1.8,
            dash="dot",
            color="rgba(99,102,241,0.85)",
        ),
        hovertemplate=(
            "60 dk Ortalama: %{y}<br>"
            "%{x|%d.%m %H:%M}"
            "<extra></extra>"
        ),
    )

    if not analyzed_df.empty:
        latest_value = analyzed_df[column].iloc[-1]

        fig.add_annotation(
            x=analyzed_df["timestamp"].iloc[-1],
            y=latest_value,
            text=f"{latest_value:.{precision}f}",
            showarrow=True,
            arrowhead=0,
            ax=-30,
            ay=-35,
            font=dict(
                size=11,
                color="#F8FAFC",
            ),
            bgcolor=line_color,
            bordercolor="rgba(255,255,255,0.12)",
            borderwidth=1,
            borderpad=5,
        )

    fig.update_layout(
        height=320,

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        margin=dict(
            l=10,
            r=10,
            t=28,
            b=10,
        ),

        hovermode="x unified",

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0,
            font=dict(
                size=10,
                color="#94A3B8",
            ),
            bgcolor="rgba(0,0,0,0)",
        ),

        xaxis=dict(
            title="",
            showgrid=False,
            zeroline=False,
            showline=False,
            tickfont=dict(
                size=10,
                color="#64748B",
            ),
        ),

        yaxis=dict(
            title="",
            showgrid=True,
            gridcolor="rgba(148,163,184,0.08)",
            zeroline=False,
            showline=False,
            tickfont=dict(
                size=10,
                color="#64748B",
            ),
        ),

        font=dict(
            family="Arial",
            color="#CBD5E1",
        ),
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={
            "displayModeBar": False,
            "scrollZoom": False,
        },
    )

    show_statistics(
        df,
        column,
        suffix,
    )

df = df_all.copy()

filter_header_html = (
    '<div style="margin-top:28px;margin-bottom:12px;">'
    '<div style="'
    'color:#64748B;'
    'font-size:10px;'
    'font-weight:800;'
    'letter-spacing:1.5px;'
    '">'
    'VERİ FİLTRELERİ'
    '</div>'
    '<div style="'
    'color:#F8FAFC;'
    'font-size:16px;'
    'font-weight:800;'
    'margin-top:4px;'
    '">'
    'Zaman Aralığı'
    '</div>'
    '<div style="'
    'color:#94A3B8;'
    'font-size:11px;'
    'line-height:1.5;'
    'margin-top:5px;'
    '">'
    'Grafik ve istatistiklerde görüntülenecek veri dönemini seçin.'
    '</div>'
    '</div>'
)

st.sidebar.markdown(
    filter_header_html,
    unsafe_allow_html=True,
)

period = st.sidebar.selectbox(
    "Görüntülenecek Dönem",
    (
        "Tüm Veriler",
        "Son 1 Saat",
        "Son 24 Saat",
        "Son 7 Gün",
    ),
    key="market_period_filter",
)

now = datetime.now()

if period == "Son 1 Saat":
    df = df[df["timestamp"] >= now - timedelta(hours=1)]
elif period == "Son 24 Saat":
    df = df[df["timestamp"] >= now - timedelta(days=1)]
elif period == "Son 7 Gün":
    df = df[df["timestamp"] >= now - timedelta(days=7)]

if df.empty:

    st.info(
        "Seçilen zaman aralığında veri bulunmuyor."
    )

else:

    # =====================================================
    # ALTIN ANALİZİ
    # =====================================================

    gold_section_html = (
        '<div style="margin-top:10px;margin-bottom:24px;">'
        '<div style="color:#64748B;font-size:10px;font-weight:800;'
        'letter-spacing:1.5px;">DEĞERLİ METALLER</div>'
        '<div style="color:#F8FAFC;font-size:27px;font-weight:800;'
        'letter-spacing:-0.6px;margin-top:4px;">Altın Analizi</div>'
        '<div style="color:#94A3B8;font-size:12px;margin-top:5px;">'
        'Gram ve ons altındaki fiyat hareketlerini, trendleri ve '
        'istatistikleri inceleyin.'
        '</div>'
        '</div>'
    )

    st.markdown(
        gold_section_html,
        unsafe_allow_html=True,
    )

    gold_col1, gold_col2 = st.columns(
        2,
        gap="large",
    )

    with gold_col1:

            with st.container(border=True):
                show_market_chart(
                    df=df,
                    column="gold_gram",
                    title="Gram Altın",
                    suffix="TL",
                    line_color="#FACC15",
                    precision=2,
                )

    with gold_col2:

            with st.container(border=True):
                show_market_chart(
                    df=df,
                    column="gold_ounce",
                    title="Ons Altın",
                    suffix="$",
                    line_color="#FB923C",
                    precision=2,
                )


    st.markdown(
        '<div style="height:1px;'
        'background:linear-gradient(90deg,transparent,rgba(255,255,255,0.08),transparent);'
        'margin:38px 0 30px 0;"></div>',
        unsafe_allow_html=True,
    )


    # =====================================================
    # DÖVİZ ANALİZİ
    # =====================================================

    fx_section_html = (
        '<div style="margin-top:10px;margin-bottom:24px;">'
        '<div style="color:#64748B;font-size:10px;font-weight:800;'
        'letter-spacing:1.5px;">DÖVİZ PİYASASI</div>'
        '<div style="color:#F8FAFC;font-size:27px;font-weight:800;'
        'letter-spacing:-0.6px;margin-top:4px;">Döviz Analizi</div>'
        '<div style="color:#94A3B8;font-size:12px;margin-top:5px;">'
        'USD, EUR ve GBP kurlarındaki kısa ve orta vadeli piyasa '
        'hareketlerini takip edin.'
        '</div>'
        '</div>'
    )

    st.markdown(
        fx_section_html,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        show_market_chart(
            df=df,
            column="usd_try",
            title="USD / TRY",
            suffix="TL",
            line_color="#22D3EE",
            precision=4,
        )

    st.markdown(
        '<div style="height:18px;"></div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        show_market_chart(
            df=df,
            column="eur_try",
            title="EUR / TRY",
            suffix="TL",
            line_color="#60A5FA",
            precision=4,
        )

    st.markdown(
        '<div style="height:18px;"></div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        show_market_chart(
            df=df,
            column="gbp_try",
            title="GBP / TRY",
            suffix="TL",
            line_color="#A78BFA",
            precision=4,
        )

st.markdown(
    '<div style="height:1px;'
    'background:linear-gradient(90deg,transparent,rgba(255,255,255,0.08),transparent);'
    'margin:40px 0 28px 0;"></div>',
    unsafe_allow_html=True,
)

# =====================================================
# MARKET DATA
# =====================================================

df_table = df.sort_values(
    "timestamp",
    ascending=False,
).copy()

record_count = len(df_table)

database_header_html = (
    '<div style="margin-top:10px;margin-bottom:18px;">'
    '<div style="'
    'color:#64748B;'
    'font-size:10px;'
    'font-weight:800;'
    'letter-spacing:1.6px;'
    '">'
    'PİYASA VERİTABANI'
    '</div>'
    '<div style="'
    'color:#F8FAFC;'
    'font-size:27px;'
    'font-weight:800;'
    'letter-spacing:-0.6px;'
    'margin-top:4px;'
    '">'
    'Piyasa Verileri'
    '</div>'
    '<div style="'
    'color:#94A3B8;'
    'font-size:12px;'
    'margin-top:5px;'
    '">'
    'Kaydedilen geçmiş döviz ve altın piyasa verilerini inceleyin '
    'veya CSV formatında dışa aktarın.'
    '</div>'
    '</div>'
)

st.markdown(
    database_header_html,
    unsafe_allow_html=True,
)

info_col1, info_col2, info_col3 = st.columns(
    3,
    gap="medium",
)


def database_info_card(label, value):

    card_html = (
        '<div style="'
        'padding:16px 18px;'
        'border-radius:14px;'
        'border:1px solid rgba(255,255,255,0.07);'
        'background:rgba(15,23,42,0.65);'
        'min-height:82px;'
        '">'
        '<div style="'
        'color:#64748B;'
        'font-size:9px;'
        'font-weight:800;'
        'letter-spacing:1.2px;'
        '">'
        f'{label}'
        '</div>'
        '<div style="'
        'color:#F8FAFC;'
        'font-size:18px;'
        'font-weight:800;'
        'margin-top:8px;'
        '">'
        f'{value}'
        '</div>'
        '</div>'
    )

    st.markdown(
        card_html,
        unsafe_allow_html=True,
    )


with info_col1:

    database_info_card(
        "TOPLAM KAYIT",
        record_count,
    )


with info_col2:

    database_info_card(
        "SON GÜNCELLEME",
        formatted_time,
    )


with info_col3:

    database_info_card(
        "TAKİP EDİLEN VARLIK",
        "5",
    )

st.markdown(
    '<div style="height:14px;"></div>',
    unsafe_allow_html=True,
)

display_df = df_table.rename(
    columns={
        "id": "ID",
        "timestamp": "Tarih / Saat",
        "usd_try": "USD / TRY",
        "eur_try": "EUR / TRY",
        "gbp_try": "GBP / TRY",
        "gold_ounce": "Ons Altın ($)",
        "gold_gram": "Gram Altın (TL)",
    }
)

st.dataframe(
    display_df,
    width="stretch",
    hide_index=True,
)

temp_df = df_table.copy()

if "timestamp" in temp_df.columns:
    temp_df["timestamp"] = temp_df["timestamp"].astype(str)

csv_data = temp_df.to_csv(
    index=False
).encode("utf-8-sig")

st.markdown(
    '<div style="height:8px;"></div>',
    unsafe_allow_html=True,
)

st.download_button(
    label="↓  Piyasa Verilerini CSV Olarak İndir",
    data=csv_data,
    file_name=(
        f"market_data_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    ),
    mime="text/csv",
    use_container_width=True,
)