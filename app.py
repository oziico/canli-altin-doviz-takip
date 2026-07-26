import os
import platform
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

from alerts import (
    ALERT_NAME_MAP,
    get_new_alert,
    should_show_alert,
    dismiss_alert,
    should_play_alarm_sound,
    mark_alarm_sound_as_played,
)

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

if platform.system() == "Darwin":
    os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

st.set_page_config(
    page_title="Canlı Altın ve Döviz Takip Sistemi",
    page_icon="📈",
    layout="wide",
)

st.markdown(
    """

<style>
:root {
    --text: #0F172A;
    --muted: #64748B;
    --border: #DCE4EE;
    --blue: #2563EB;
    --green: #059669;
    --red: #DC2626;
}

html,
body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background: #FFFFFF !important;
    color: var(--text) !important;
}

header[data-testid="stHeader"],
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
section[data-testid="stSidebar"],
button[data-testid="stSidebarCollapseButton"],
div[data-testid="collapsedControl"] {
    display: none !important;
}

.block-container,
[data-testid="stMainBlockContainer"] {
    width: 100% !important;
    max-width: 1520px !important;
    padding: 44px 3rem 4rem !important;
}

/* SABİT KAYAN PİYASA BANDI */
.top-ticker {
    position: fixed;
    inset: 0 0 auto 0;
    z-index: 999999;
    height: 44px;
    display: flex;
    align-items: center;
    overflow: hidden;
    background: #0F172A;
    border-bottom: 1px solid #1E293B;
    box-shadow: 0 4px 14px rgba(15, 23, 42, .14);
    white-space: nowrap;
}

.top-ticker-label {
    flex: 0 0 auto;
    height: 44px;
    display: inline-flex;
    align-items: center;
    padding: 0 18px;
    background: #111C31;
    border-right: 1px solid rgba(255, 255, 255, .10);
    color: #E2E8F0;
    font-size: 13px;
    font-weight: 850;
    letter-spacing: .7px;
}

.top-ticker-window {
    flex: 1;
    min-width: 0;
    overflow: hidden;
}

.top-ticker-track {
    display: inline-flex;
    align-items: center;
    width: max-content;
    padding-left: 100%;
    animation: tickerScroll 34s linear infinite;
}

.top-ticker:hover .top-ticker-track {
    animation-play-state: paused;
}

@keyframes tickerScroll {
    from { transform: translateX(0); }
    to { transform: translateX(-50%); }
}

.ticker-item {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-right: 52px;
    font-size: 14px;
    font-weight: 750;
}

.ticker-price { color: #F8FAFC; }
.ticker-up { color: #22C55E; }
.ticker-down { color: #F87171; }

/* HERO */
.hero-card {
    width: 100% !important;
    margin: 0 0 12px !important;
    padding: 28px 3.2rem 26px !important;
    overflow: hidden;
    border: 1px solid #D5DFEC !important;
    border-radius: 10px !important;
    background:
        radial-gradient(circle at 82% 20%, rgba(14, 165, 233, .10), transparent 30%),
        radial-gradient(circle at 58% 120%, rgba(124, 58, 237, .09), transparent 34%),
        linear-gradient(90deg, #F3F7FF 0%, #F7F5FF 52%, #EEF8FF 100%) !important;
    box-shadow: 0 8px 24px rgba(15, 23, 42, .045) !important;
}

.hero-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 24px;
}

.hero-eyebrow {
    margin-bottom: 7px;
    color: #4F46E5;
    font-size: 13px;
    font-weight: 850;
    letter-spacing: 1.4px;
}

.hero-title {
    color: var(--text);
    font-size: clamp(30px, 3vw, 40px);
    font-weight: 850;
    line-height: 1.12;
    letter-spacing: -.8px;
}

.hero-subtitle {
    max-width: 820px;
    margin-top: 9px;
    color: #475569;
    font-size: 16px;
    font-weight: 500;
    line-height: 1.65;
}

.live-pill {
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    gap: 9px;
    padding: 9px 14px;
    border: 1px solid rgba(5, 150, 105, .20);
    border-radius: 999px;
    background: #ECFDF5;
    color: #047857;
    font-size: 12px;
    font-weight: 850;
}

.live-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #10B981;
    box-shadow: 0 0 0 4px rgba(16, 185, 129, .12);
}

/* BAŞLIKLAR */
.section-kicker {
    margin: 20px 0 14px;
    font-size: 15px;
    font-weight: 850;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.section-prices { color: #0369A1; }
.section-summary { color: #6D28D9; }

.price-group-title {
    margin: 18px 0 8px;
    font-size: 18px;
    font-weight: 850;
}

.price-group-title.fx { color: #1D4ED8; }
.price-group-title.gold { color: #B45309; }

/* FİYAT KARTLARI */
.price-strip {
    display: grid;
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: 14px;
    background: transparent;
    box-shadow: 0 8px 22px rgba(15, 23, 42, .055);
}

.price-strip.fx-grid { grid-template-columns: repeat(3, 1fr); }
.price-strip.gold-grid { grid-template-columns: repeat(2, 1fr); }

.price-item {
    min-height: 128px;
    padding: 22px 24px;
}

.price-item + .price-item { border-left: 1px solid #E2E8F0; }

.price-usd { background: #F5FCFD; box-shadow: inset 0 4px 0 #0891B2; }
.price-eur { background: #F6F9FF; box-shadow: inset 0 4px 0 #2563EB; }
.price-gbp { background: #FAF7FF; box-shadow: inset 0 4px 0 #7C3AED; }
.price-gram { background: #FFFDF6; box-shadow: inset 0 4px 0 #D97706; }
.price-ounce { background: #FFF9F5; box-shadow: inset 0 4px 0 #EA580C; }

.price-item-label {
    color: #475569;
    font-size: 14px;
    font-weight: 850;
    letter-spacing: .4px;
}

.price-item-value {
    margin-top: 13px;
    color: var(--text);
    font-size: 30px;
    font-weight: 850;
    line-height: 1.05;
}

.price-item-unit {
    margin-left: 5px;
    color: var(--muted);
    font-size: 12px;
    font-weight: 800;
}

.price-item-meta {
    margin-top: 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.price-change-up,
.price-change-down {
    padding: 5px 8px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 850;
}

.price-change-up { color: #047857; background: #ECFDF5; }
.price-change-down { color: #B91C1C; background: #FEF2F2; }

.price-vol {
    color: var(--muted);
    font-size: 11px;
    font-weight: 750;
}

/* GENEL KARTLAR */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 14px 16px 18px !important;
    box-shadow: 0 8px 22px rgba(15, 23, 42, .055) !important;
}

/* ALARM MERKEZİ */
.alarm-section-title {
    margin: 18px 0 10px;
    color: #1E3A8A;
    font-size: 16px;
    font-weight: 900;
    letter-spacing: .7px;
}

.alarm-panel-title {
    margin-bottom: 14px;
    color: #16213A;
    font-size: 17px;
    font-weight: 900;
}

.st-key-alarm_create_card {
    background: linear-gradient(145deg, #F5F9FF 0%, #EEF5FF 100%) !important;
    border: 1.5px solid #8CB4FF !important;
}

.st-key-active_alerts_card,
.st-key-alert_history_card {
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
}

.st-key-alarm_create_card div[data-baseweb="select"] > div,
.st-key-alarm_create_card div[data-baseweb="input"] > div,
.st-key-alarm_create_card input {
    min-height: 42px !important;
    background: #FFFFFF !important;
    color: var(--text) !important;
    border: 1px solid #B7C9E5 !important;
    border-radius: 7px !important;
    box-shadow: none !important;
}

.st-key-alarm_create_card div[data-baseweb="select"] *,
.st-key-alarm_create_card input {
    color: var(--text) !important;
    -webkit-text-fill-color: var(--text) !important;
}

.st-key-alarm_create_card label {
    color: #475569 !important;
    font-size: 11px !important;
    font-weight: 850 !important;
}

.st-key-alarm_create_card button[kind="primary"] {
    min-height: 42px !important;
    border: 0 !important;
    border-radius: 7px !important;
    background: linear-gradient(135deg, #1769F5, #0755E8) !important;
    color: #FFFFFF !important;
    font-weight: 850 !important;
    box-shadow: 0 6px 16px rgba(37, 99, 235, .22) !important;
}

.alarm-field-label {
    margin-bottom: 7px;
    color: #475569;
    font-size: 11px;
    font-weight: 850;
}

.alarm-current-price {
    min-height: 42px;
    display: flex;
    align-items: center;
    padding: 0 13px;
    background: #FFFFFF;
    color: var(--text);
    border: 1px solid #B7C9E5;
    border-radius: 7px;
    font-size: 14px;
    font-weight: 850;
}

.alarm-helper {
    margin-top: 14px;
    padding: 11px 13px;
    border: 1px solid #DBEAFE;
    border-radius: 8px;
    background: #EEF5FF;
    color: #1D4ED8;
    font-size: 12px;
}

.active-alarm-row,
.history-alarm-row {
    margin-bottom: 7px;
    padding: 11px 12px;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    background: #FFFFFF;
}

.active-alarm-row { border-left: 4px solid #2563EB; }
.history-alarm-row { border-left: 4px solid #10B981; }

.alarm-row-top,
.alarm-row-bottom {
    display: flex;
    justify-content: space-between;
    gap: 10px;
}

.alarm-row-top {
    color: #172033;
    font-size: 13px;
    font-weight: 900;
}

.alarm-row-bottom {
    margin-top: 4px;
    color: var(--muted);
    font-size: 11px;
}

.alarm-condition-up { color: #059669; font-weight: 850; }
.alarm-condition-down { color: #DC2626; font-weight: 850; }

.alarm-empty {
    padding: 16px;
    border: 1px dashed #CBD5E1;
    border-radius: 8px;
    background: #F8FAFC;
    color: var(--muted);
    font-size: 12px;
    text-align: center;
}

/* PİYASA ÖZETİ */
.insight-card {
    min-height: 125px;
    padding: 20px;
    border: 1px solid var(--border);
    border-radius: 16px;
    background: #FFFFFF;
    box-shadow: 0 8px 22px rgba(15, 23, 42, .055);
}

.insight-label {
    color: var(--muted);
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.insight-value {
    margin-top: 10px;
    color: var(--text);
    font-size: 19px;
    font-weight: 800;
}

.insight-positive { margin-top: 6px; color: #047857; font-size: 14px; font-weight: 700; }
.insight-negative { margin-top: 6px; color: #B91C1C; font-size: 14px; font-weight: 700; }
.insight-neutral { margin-top: 6px; color: #475569; font-size: 14px; font-weight: 700; }

/* FORM ELEMANLARI */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
input {
    background: #FFFFFF !important;
    color: var(--text) !important;
    border-color: #CBD5E1 !important;
}

label {
    color: #334155 !important;
}

/* TABLO VE İNDİRME */
div[data-testid="stDataFrame"],
div[data-testid="stDataFrame"] > div {
    background: #FFFFFF !important;
    border-color: var(--border) !important;
}

.stDownloadButton > button {
    background: #FFFFFF !important;
    color: var(--text) !important;
    border: 1px solid #CBD5E1 !important;
}

.stDownloadButton > button:hover {
    background: #F8FAFC !important;
}

/* MOBİL */
@media (max-width: 850px) {
    .block-container,
    [data-testid="stMainBlockContainer"] {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .hero-card {
        padding: 22px 1.25rem !important;
    }

    .hero-top {
        flex-direction: column;
        align-items: flex-start;
    }

    .hero-title { font-size: 29px; }
    .hero-subtitle { font-size: 15px; }

    .price-strip.fx-grid,
    .price-strip.gold-grid {
        grid-template-columns: 1fr;
    }

    .price-item + .price-item {
        border-left: 0;
        border-top: 1px solid #E2E8F0;
    }

    .top-ticker-label {
        padding: 0 12px;
        font-size: 11px;
    }

    .ticker-item {
        margin-right: 34px;
        font-size: 12px;
    }
}

/* Streamlit uyarı mesajlarının yazı renkleri */

div[data-testid="stAlert"] {
    color: #7C5A00 !important;
}

div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span,
div[data-testid="stAlert"] div {
    color: #7C5A00 !important;
}

/* Hata mesajı */
div[data-testid="stAlert"][data-baseweb="notification"] {
    font-weight: 700;
}

/* Aktif alarm silme butonu */

.st-key-active_alerts_card button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #1F2937 !important;
    border: 1px solid #D1D5DB !important;
    transition: all .2s ease;
}

.st-key-active_alerts_card button[kind="secondary"]:hover {
    background: #EF4444 !important;
    color: white !important;
    border-color: #EF4444 !important;
}

</style>

""",
    unsafe_allow_html=True,
)

METRICS = [
    "usd_try",
    "eur_try",
    "gbp_try",
    "gold_ounce",
    "gold_gram",
]

NAME_MAP = {
    "usd_try": "USD / TRY",
    "eur_try": "EUR / TRY",
    "gbp_try": "GBP / TRY",
    "gold_ounce": "Ons Altın ($)",
    "gold_gram": "Gram Altın (TL)",
}

TICKER_ASSETS = [
    ("USD / TRY", "usd_try"),
    ("EUR / TRY", "eur_try"),
    ("GBP / TRY", "gbp_try"),
    ("Gram Altın", "gold_gram"),
    ("Ons Altın", "gold_ounce"),
]

def build_price_item(
    metric,
    label,
    value,
    unit,
    css_class,
    changes,
    volatilities,
):
    change = changes[metric]["pct"]
    volatility = volatilities[metric]

    if change >= 0:
        change_class = "price-change-up"
        change_icon = "↗"
    else:
        change_class = "price-change-down"
        change_icon = "↘"

    return (
        f'<div class="price-item {css_class}">'
        f'<div class="price-item-label">{label}</div>'
        f'<div class="price-item-value">{value}'
        f'<span class="price-item-unit">{unit}</span></div>'
        '<div class="price-item-meta">'
        f'<span class="{change_class}">'
        f'{change_icon} {abs(change):.2f}%'
        '</span>'
        f'<span class="price-vol">'
        f'VOL {volatility:.2f}%'
        '</span>'
        '</div>'
        '</div>'
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
            "soft": "#ECFDF5",
        },
        {
            "label": "EN DÜŞÜK",
            "value": val_min,
            "accent": "#FB7185",
            "soft": "#FEF2F2",
        },
        {
            "label": "ORTALAMA",
            "value": val_avg,
            "accent": "#60A5FA",
            "soft": "#EFF6FF",
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
            'border:1px solid #DCE4EE;'
            f'background:{card["soft"]};'
            'min-height:82px;'
            'display:flex;'
            'flex-direction:column;'
            'justify-content:center;'
            '">'
            f'<div style="'
            f'color:{card["accent"]};'
            'font-size:13px;'
            'font-weight:800;'
            'letter-spacing:1px;'
            '">'
            f'{card["label"]}'
            '</div>'
            '<div style="'
            'margin-top:7px;'
            'color:#0F172A;'
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
        trend_color = "#059669"
        trend_bg = "#ECFDF5"

    elif trend == "Düşüş Eğilimi":
        trend_text = "DÜŞÜŞ"
        trend_icon = "↘"
        trend_color = "#DC2626"
        trend_bg = "#FEF2F2"

    elif trend == "Yetersiz Veri":
        trend_text = "VERİ BİRİKİYOR"
        trend_icon = "◌"
        trend_color = "#B45309"
        trend_bg = "#FFFBEB"

    else:
        trend_text = "YATAY"
        trend_icon = "→"
        trend_color = "#475569"
        trend_bg = "#F1F5F9"

    chart_header = (
        '<div style="'
        'display:flex;'
        'justify-content:space-between;'
        'align-items:center;'
        'margin-bottom:10px;'
        '">'
        '<div>'
        '<div style="'
        'font-size:21px;'
        'font-weight:800;'
        'color:#0F172A;'
        '">'
        f'{title}'
        '</div>'
        '<div style="'
        'margin-top:4px;'
        'font-size:14px;'
        'color:#475569;'
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
        'font-size:13px;'
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
                size=12,
                color="#FFFFFF",
            ),
            bgcolor=line_color,
            bordercolor="rgba(255,255,255,0.12)",
            borderwidth=1,
            borderpad=5,
        )

    chart_backgrounds = {
        "gold_gram": "#FFFDF6",
        "gold_ounce": "#FFF9F5",
        "usd_try": "#F5FCFD",
        "eur_try": "#F6F9FF",
        "gbp_try": "#FAF7FF",
    }

    fig.update_layout(
        height=320,

        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor=chart_backgrounds.get(column, "#FFFFFF"),

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
                color="#475569",
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
            gridcolor="#E2E8F0",
            zeroline=False,
            showline=False,
            tickfont=dict(
                size=10,
                color="#64748B",
            ),
        ),

        font=dict(
            family="Arial",
            color="#334155",
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

def database_info_card(label, value):

    card_html = (
        '<div style="'
        'padding:16px 18px;'
        'border-radius:14px;'
        'border:1px solid #DCE4EE;'
        'background:#FFFFFF;'
        'min-height:82px;'
        '">'
        '<div style="'
        'color:#475569;'
        'font-size:12px;'
        'font-weight:800;'
        'letter-spacing:1.2px;'
        '">'
        f'{label}'
        '</div>'
        '<div style="'
        'color:#0F172A;'
        'font-size:21px;'
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
        last_alert["metric"],
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
        .st-key-triggered_alarm_banner {
            background: #FFFFFF !important;
            border: 1px solid #FCA5A5 !important;
            border-left: 6px solid #EF4444 !important;
            border-radius: 14px !important;
            padding: 12px 16px !important;
            box-shadow: 0 10px 26px rgba(15, 23, 42, 0.10) !important;
        }

        .st-key-triggered_alarm_banner .alarm-wrapper {
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
        }

        .st-key-triggered_alarm_banner .alarm-header {
            margin-bottom: 10px !important;
            color: #DC2626 !important;
            font-size: 18px !important;
            font-weight: 850 !important;
            line-height: 1.3 !important;
        }

        .st-key-triggered_alarm_banner .alarm-asset {
            margin-bottom: 7px !important;
            color: #0F172A !important;
            font-size: 17px !important;
            font-weight: 850 !important;
        }

        .st-key-triggered_alarm_banner .alarm-info {
            color: #475569 !important;
            font-size: 14px !important;
            line-height: 1.5 !important;
            margin-bottom: 18px !important;
        }

        .st-key-triggered_alarm_banner .alarm-current {
            color: #0F172A !important;
            font-weight: 850 !important;
        }

        .st-key-triggered_alarm_banner .alarm-target {
            color: #D97706 !important;
            font-weight: 850 !important;
        }

        .st-key-triggered_alarm_banner button {
            width: 40px !important;
            min-width: 40px !important;
            height: 40px !important;
            min-height: 40px !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            background: #FFFFFF !important;
            color: #64748B !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 10px !important;
            box-shadow: none !important;
        }

        .st-key-triggered_alarm_banner button:hover {
            background: #FEF2F2 !important;
            color: #DC2626 !important;
            border-color: #FCA5A5 !important;
        }

        .st-key-triggered_alarm_banner button p {
            margin: 0 !important;
            padding: 0 !important;
            color: inherit !important;
            font-size: 18px !important;
            line-height: 1 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container(
        border=True,
        key="triggered_alarm_banner",
    ):
        content_col, close_col = st.columns(
            [18, 1],
            vertical_alignment="top",
        )

        with content_col:
            alarm_html = (
                '<div class="alarm-wrapper">'
                '<div class="alarm-header">'
                '🚨 Fiyat Alarmı Tetiklendi'
                '</div>'
                f'<div class="alarm-asset">{alert_name}</div>'
                '<div class="alarm-info">'
                'Güncel Fiyat: '
                f'<span class="alarm-current">'
                f'{last_alert["current_value"]:.4f}'
                '</span>'
                '<br>'
                'Alarm Koşulu: '
                f'<span class="alarm-target">'
                f'{last_alert["condition"]} '
                f'{last_alert["target_value"]:.4f}'
                '</span>'
                '</div>'
                '</div>'
            )

            st.markdown(
                alarm_html,
                unsafe_allow_html=True,
            )

        with close_col:
            st.markdown(
                "<div style='height:6px'></div>",
                unsafe_allow_html=True,
            )

            if st.button(
                "✕",
                key=f"dismiss_alert_{alert_id}",
                help="Kapat",
                type="secondary",
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

last_update_html = (
    '<div style="background:#FFFFFF;padding:11px 16px;border:1px solid #DCE4EE;'
    'border-left:4px solid #2563EB;display:flex;align-items:center;gap:9px;'
    'margin-top:8px;margin-bottom:16px;box-shadow:0 4px 14px rgba(15,23,42,0.04);">'
    '<span style="font-size:14px;color:#475569;font-weight:700;">SON VERİ GİRİŞİ</span>'
    f'<strong style="font-size:14px;color:#0F172A;font-weight:800;">{formatted_time}</strong>'
    '</div>'
)

st.markdown(last_update_html, unsafe_allow_html=True)

changes_24h, volatility_24h = calculate_24h_analysis(
    df_all,
    latest,
    METRICS,
)

ticker_items = []

for _ in range(2):
    for title, key in TICKER_ASSETS:
        value = latest[key]
        change = changes_24h[key]["pct"]

        if change >= 0:
            arrow = "▲"
            cls = "ticker-up"
        else:
            arrow = "▼"
            cls = "ticker-down"

        value_text = f"{value:.2f}" if "gold" in key else f"{value:.4f}"

        ticker_items.append(
            f'<span class="ticker-item">'
            f'<span class="ticker-price">{title}</span>'
            f'<span class="ticker-price">{value_text}</span>'
            f'<span class="{cls}">{arrow} {abs(change):.2f}%</span>'
            f'</span>'
        )

ticker_html = (
    '<div class="top-ticker">'
    '<div class="top-ticker-label">📡 CANLI PİYASA</div>'
    '<div class="top-ticker-window">'
    '<div class="top-ticker-track">'
    + "".join(ticker_items)
    + '</div></div></div>'
)

st.markdown(
    ticker_html,
    unsafe_allow_html=True,
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

st.markdown(
    '<div class="section-kicker section-prices" style="margin-top:18px;">'
    'CANLI PİYASA FİYATLARI'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="price-group-title fx">DÖVİZ</div>',
    unsafe_allow_html=True,
)

fx_prices_html = (
    '<div class="price-strip fx-grid">'
    + build_price_item(
        "usd_try",
        "ABD DOLARI",
        f"{latest['usd_try']:.4f}",
        "TRY",
        "price-usd",
        changes_24h,
        volatility_24h,
    )
    + build_price_item(
        "eur_try",
        "EURO",
        f"{latest['eur_try']:.4f}",
        "TRY",
        "price-eur",
        changes_24h,
        volatility_24h,
    )
    + build_price_item(
        "gbp_try",
        "İNGİLİZ STERLİNİ",
        f"{latest['gbp_try']:.4f}",
        "TRY",
        "price-gbp",
        changes_24h,
        volatility_24h,
    )
    + '</div>'
)

st.markdown(
    fx_prices_html,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="price-group-title gold">ALTIN</div>',
    unsafe_allow_html=True,
)

gold_prices_html = (
    '<div class="price-strip gold-grid">'
    + build_price_item(
        "gold_gram",
        "GRAM ALTIN",
        f"{latest['gold_gram']:.2f}",
        "TRY",
        "price-gram",
        changes_24h,
        volatility_24h,
    )
    + build_price_item(
        "gold_ounce",
        "ONS ALTIN",
        f"{latest['gold_ounce']:.2f}",
        "USD",
        "price-ounce",
        changes_24h,
        volatility_24h,
    )
    + '</div>'
)

st.markdown(
    gold_prices_html,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="alarm-section-title">ALARM MERKEZİ</div>',
    unsafe_allow_html=True,
)

alarm_form_col, active_alarm_col, history_col = st.columns(
    [1.15, 1, 1],
    gap="small",
)

with alarm_form_col:
    with st.container(
        border=True,
        height=355,
        key="alarm_create_card",
    ):
        st.markdown(
            '<div class="alarm-panel-title">🔔 Alarm Merkezi</div>',
            unsafe_allow_html=True,
        )

        asset_col, current_col, condition_col = st.columns(
            [1.1, 0.9, 1.2],
            gap="small",
        )

        with asset_col:
            alert_metric = st.selectbox(
                "VARLIK",
                options=METRICS,
                format_func=lambda x: NAME_MAP[x],
                key="main_alert_metric_select",
            )

        current_asset_value = float(latest[alert_metric])

        with current_col:
            st.markdown(
                '<div class="alarm-field-label">MEVCUT FİYAT</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                (
                    '<div class="alarm-current-price">'
                    f'{current_asset_value:.4f}'
                    '</div>'
                ),
                unsafe_allow_html=True,
            )

        with condition_col:
            alert_condition = st.selectbox(
                "KOŞUL",
                options=[">", "<"],
                format_func=lambda value: (
                    "↗ Üzerine çıkarsa"
                    if value == ">"
                    else "↘ Altına düşerse"
                ),
                key="main_alert_condition",
            )

        target_col, button_col = st.columns(
            [1.35, 1],
            gap="small",
            vertical_alignment="bottom",
        )

        with target_col:
            alert_target_str = st.text_input(
                "HEDEF FİYAT",
                value=f"{current_asset_value:.4f}",
                key=f"main_target_input_{alert_metric}",
            )

        with button_col:
            create_alarm_clicked = st.button(
                "＋ ALARM OLUŞTUR",
                use_container_width=True,
                type="primary",
                key="main_create_alert",
            )

        if create_alarm_clicked:
            try:
                alert_target = float(alert_target_str)

                is_already_passed = (
                    alert_condition == ">"
                    and current_asset_value > alert_target
                ) or (
                    alert_condition == "<"
                    and current_asset_value < alert_target
                )

                if is_already_passed:
                    direction_text = (
                        "üzerinde"
                        if alert_condition == ">"
                        else "altında"
                    )

                    st.warning(
                        "Mevcut fiyat zaten hedef değerin "
                        f"{direction_text}. Farklı bir hedef girin."
                    )

                elif alert_exists(
                    alert_metric,
                    alert_condition,
                    alert_target,
                ):
                    st.warning(
                        "Bu kriterlere sahip aktif bir alarm zaten mevcut."
                    )

                else:
                    insert_alert(
                        alert_metric,
                        alert_condition,
                        alert_target,
                    )

                    st.success(
                        f"Alarm oluşturuldu: {NAME_MAP[alert_metric]} "
                        f"{alert_condition} {alert_target:.4f}"
                    )

                    st.rerun()

            except ValueError:
                st.error("Lütfen geçerli bir hedef fiyat girin.")

        st.markdown(
            (
                '<div class="alarm-helper">'
                'ⓘ Belirlediğiniz koşul gerçekleştiğinde '
                'anlık bildirim alırsınız.'
                '</div>'
            ),
            unsafe_allow_html=True,
        )


with active_alarm_col:
    with st.container(
        border=True,
        height=355,
        key="active_alerts_card",
    ):
        current_active = get_active_alerts()

        st.markdown(
            f'<div class="alarm-panel-title">↗ Aktif Alarmlar ({len(current_active)})</div>',
            unsafe_allow_html=True,
        )

        if not current_active:
            st.markdown(
                '<div class="alarm-empty">Bekleyen aktif alarm bulunmuyor.</div>',
                unsafe_allow_html=True,
            )
        else:
            for act in current_active[:5]:
                asset_name = NAME_MAP[act["metric"]]
                is_above = act["condition"] == ">"
                condition_text = (
                    "Üzerine çıkarsa"
                    if is_above
                    else "Altına düşerse"
                )
                condition_class = (
                    "alarm-condition-up"
                    if is_above
                    else "alarm-condition-down"
                )
                current_value = float(latest[act["metric"]])

                row_col, delete_col = st.columns(
                    [7, 1],
                    vertical_alignment="center",
                )

                with row_col:
                    st.markdown(
                        (
                            '<div class="active-alarm-row">'
                            '<div class="alarm-row-top">'
                            f'<span>{asset_name}</span>'
                            f'<span>{act["target_value"]:.4f}</span>'
                            '</div>'
                            '<div class="alarm-row-bottom">'
                            f'<span class="{condition_class}">{condition_text}</span>'
                            f'<span>Mevcut: {current_value:.4f}</span>'
                            '</div>'
                            '</div>'
                        ),
                        unsafe_allow_html=True,
                    )

                with delete_col:
                    if st.button(
                        "🗑",
                        key=f"main_del_{act['id']}",
                        help="Alarmı sil",
                        use_container_width=True,
                    ):
                        delete_alert(act["id"])
                        st.rerun()

with history_col:
    with st.container(
        border=True,
        height=355,
        key="alert_history_card",
    ):
        history = get_alert_history()

        st.markdown(
            '<div class="alarm-panel-title">◷ Alarm Geçmişi</div>',
            unsafe_allow_html=True,
        )

        if not history:
            st.markdown(
                '<div class="alarm-empty">Henüz tetiklenen alarm bulunmuyor.</div>',
                unsafe_allow_html=True,
            )
        else:
            for item in history[:4]:
                asset_name = NAME_MAP[item["metric"]]
                is_above = item["condition"] == ">"
                direction = "Üzerine çıktı" if is_above else "Altına düştü"
                condition_class = (
                    "alarm-condition-up"
                    if is_above
                    else "alarm-condition-down"
                )

                st.markdown(
                    (
                        '<div class="history-alarm-row">'
                        '<div class="alarm-row-top">'
                        f'<span>{asset_name}</span>'
                        f'<span>{item["target_value"]:.4f}</span>'
                        '</div>'
                        '<div class="alarm-row-bottom">'
                        f'<span class="{condition_class}">{direction}</span>'
                        f'<span>{item["triggered_at"]}</span>'
                        '</div>'
                        '</div>'
                    ),
                    unsafe_allow_html=True,
                )


st.markdown(
    '<div class="section-kicker section-summary" style="margin-top:28px;">PİYASA ÖZETİ</div>',
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

loser_pct = max_dropped[1]["pct"]

loser_class = (
    "insight-negative"
    if loser_pct < 0
    else "insight-positive"
)

insight_cards = [
    {
        "label": "En Güçlü Varlık",
        "value": NAME_MAP[max_gained[0]],
        "detail": f'↗ {max_gained[1]["pct"]:.2f}%',
        "detail_class": "insight-positive",
    },
    {
        "label": "En Zayıf Varlık",
        "value": NAME_MAP[max_dropped[0]],
        "detail": f"{loser_pct:.2f}%",
        "detail_class": loser_class,
    },
    {
        "label": "Volatilite Lideri",
        "value": NAME_MAP[max_volatile_key],
        "detail": f"⚡ {max_volatility_val:.2f}% volatilite",
        "detail_class": "insight-neutral",
    },
    {
        "label": "Piyasa Görünümü",
        "value": market_mood,
        "detail": mood_text,
        "detail_class": mood_class,
    },
]

for column, card in zip(
    insight_cols,
    insight_cards,
):
    with column:
        st.markdown(
            (
                '<div class="insight-card">'
                f'<div class="insight-label">{card["label"]}</div>'
                f'<div class="insight-value">{card["value"]}</div>'
                f'<div class="{card["detail_class"]}">'
                f'{card["detail"]}'
                '</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

df = df_all.copy()

if "market_period_filter" not in st.session_state:
    st.session_state.market_period_filter = "Tüm Veriler"

period = st.session_state.market_period_filter

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

    gold_section_html = (
        '<div style="margin-top:18px;margin-bottom:24px;">'
        '<div style="color:#B45309;font-size:14px;font-weight:850;letter-spacing:1px;">DEĞERLİ METALLER</div>'
        '<div style="color:#92400E;font-size:30px;font-weight:850;letter-spacing:-0.6px;margin-top:5px;">Altın Analizi</div>'
        '<div style="color:#475569;font-size:16px;line-height:1.65;margin-top:7px;">'
        'Gram ve ons altındaki fiyat hareketlerini, trendleri ve istatistikleri rahatça inceleyin.'
        '</div></div>'
    )

    st.markdown(gold_section_html, unsafe_allow_html=True)

    gold_charts = [
        {
            "column": "gold_gram",
            "title": "Gram Altın",
            "suffix": "TL",
            "line_color": "#FACC15",
            "precision": 2,
        },
        {
            "column": "gold_ounce",
            "title": "Ons Altın",
            "suffix": "$",
            "line_color": "#FB923C",
            "precision": 2,
        },
    ]

    gold_columns = st.columns(
        len(gold_charts),
        gap="large",
    )

    for chart_column, chart_config in zip(
        gold_columns,
        gold_charts,
    ):
        with chart_column:
            with st.container(border=True):
                show_market_chart(
                    df=df,
                    column=chart_config["column"],
                    title=chart_config["title"],
                    suffix=chart_config["suffix"],
                    line_color=chart_config["line_color"],
                    precision=chart_config["precision"],
                )


    st.markdown(
        '<div style="height:1px;'
        'background:linear-gradient(90deg,transparent,#DCE4EE,transparent);'
        'margin:38px 0 30px 0;"></div>',
        unsafe_allow_html=True,
    )

fx_section_html = (
    '<div style="margin-top:18px;margin-bottom:24px;">'
    '<div style="color:#1D4ED8;font-size:14px;font-weight:850;letter-spacing:1px;">DÖVİZ PİYASASI</div>'
    '<div style="color:#1E3A8A;font-size:30px;font-weight:850;letter-spacing:-0.6px;margin-top:5px;">Döviz Analizi</div>'
    '<div style="color:#475569;font-size:16px;line-height:1.65;margin-top:7px;">'
    'USD, EUR ve GBP kurlarındaki kısa ve orta vadeli piyasa hareketlerini daha okunaklı grafiklerle takip edin.'
    '</div></div>'
)

st.markdown(
    fx_section_html,
    unsafe_allow_html=True,
)

fx_charts = [
    {
        "column": "usd_try",
        "title": "USD / TRY",
        "suffix": "TL",
        "line_color": "#22D3EE",
        "precision": 4,
    },
    {
        "column": "eur_try",
        "title": "EUR / TRY",
        "suffix": "TL",
        "line_color": "#60A5FA",
        "precision": 4,
    },
    {
        "column": "gbp_try",
        "title": "GBP / TRY",
        "suffix": "TL",
        "line_color": "#A78BFA",
        "precision": 4,
    },
]

for index, chart in enumerate(fx_charts):
    with st.container(border=True):
        show_market_chart(
            df=df,
            column=chart["column"],
            title=chart["title"],
            suffix=chart["suffix"],
            line_color=chart["line_color"],
            precision=chart["precision"],
        )

    if index < len(fx_charts) - 1:
        st.markdown(
            '<div style="height:18px;"></div>',
            unsafe_allow_html=True,
        )

st.markdown(
    '<div style="height:1px;'
    'background:linear-gradient(90deg,transparent,#DCE4EE,transparent);'
    'margin:40px 0 28px 0;"></div>',
    unsafe_allow_html=True,
)

df_table = df.sort_values(
    "timestamp",
    ascending=False,
).copy()

record_count = len(df_table)

database_header_html = (
    '<div style="margin-top:16px;margin-bottom:20px;">'
    '<div style="color:#047857;font-size:14px;font-weight:850;letter-spacing:1px;">PİYASA VERİTABANI</div>'
    '<div style="color:#065F46;font-size:30px;font-weight:850;letter-spacing:-0.6px;margin-top:5px;">Piyasa Verileri</div>'
    '<div style="color:#475569;font-size:16px;line-height:1.65;margin-top:7px;">'
    'Kaydedilen geçmiş döviz ve altın piyasa verilerini inceleyin veya CSV formatında dışa aktarın.'
    '</div></div>'
)

st.markdown(database_header_html, unsafe_allow_html=True)

info_cols = st.columns(
    3,
    gap="medium",
)

database_cards = [
    ("TOPLAM KAYIT", record_count),
    ("SON GÜNCELLEME", formatted_time),
    ("TAKİP EDİLEN VARLIK", len(METRICS)),
]

for column, (label, value) in zip(
    info_cols,
    database_cards,
):
    with column:
        database_info_card(
            label,
            value,
        )

st.markdown(
    '<div style="height:14px;"></div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="
        margin-top:18px;
        margin-bottom:6px;
        color:#475569;
        font-size:12px;
        font-weight:850;
        letter-spacing:.6px;
    ">
        GÖRÜNTÜLENECEK DÖNEM
    </div>
    """,
    unsafe_allow_html=True,
)

filter_col, _ = st.columns(
    [1.1, 3.9],
    gap="medium",
)

with filter_col:
    st.selectbox(
        "Görüntülenecek Dönem",
        (
            "Tüm Veriler",
            "Son 1 Saat",
            "Son 24 Saat",
            "Son 7 Gün",
        ),
        key="market_period_filter",
        label_visibility="collapsed",
    )

st.markdown(
    '<div style="height:8px;"></div>',
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

table_style = (
    display_df.style
    .set_properties(
        **{
            "background-color": "#FFFFFF",
            "color": "#0F172A",
            "border-color": "#E2E8F0",
        }
    )
    .set_table_styles(
        [
            {
                "selector": "th",
                "props": [
                    ("background-color", "#F8FAFC"),
                    ("color", "#334155"),
                    ("font-weight", "800"),
                    ("border-color", "#E2E8F0"),
                ],
            },
            {
                "selector": "td",
                "props": [
                    ("background-color", "#FFFFFF"),
                    ("color", "#0F172A"),
                    ("border-color", "#E2E8F0"),
                ],
            },
        ]
    )
)

st.dataframe(
    table_style,
    width="stretch",
    hide_index=True,
    height=390,
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