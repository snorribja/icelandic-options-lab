from __future__ import annotations

from datetime import date
from html import escape

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from black_scholes import (
    call_option_price,
    delta,
    gamma,
    put_option_price,
    rho,
    theta,
    vega,
)
from interest_rate_data import RiskFreeRate
from stock_data import StockData


ACCENT = "#4993F3"
COLORS = (ACCENT, "#3DBEF5", "#FBCB50", "#A78BFA", "#FB7185")
LINE_COLORS = (ACCENT, "#FBCB50", "#3DBEF5", "#A78BFA", "#FB7185")
PLOT_CONFIG = {"displaylogo": False, "responsive": True}


def configure_page(title: str) -> None:
    st.set_page_config(
        page_title=f"{title} | Icelandic Options Lab",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="auto",
    )
    st.markdown(
        """
        <style>
        :root {
            --lab-bg: #09101a;
            --lab-surface: #101823;
            --lab-secondary: #1a2432;
            --lab-border: #2b3b50;
            --lab-text: #ced5de;
            --lab-primary: #f9fafb;
            --lab-muted: #9ca6b4;
            --lab-accent: #4993f3;
            --lab-highlight: #fbcb50;
            --lab-radius: 0.75rem;
        }
        html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
            font-family: 'Inter', sans-serif;
        }
        h1, h2, h3, h4, h5, h6, [data-testid="stMetricValue"] {
            font-family: 'Geist', sans-serif;
        }
        [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background: var(--lab-bg);
        }
        [data-testid="stHeader"] {
            border-bottom: 1px solid var(--lab-border);
            min-height: 4rem;
        }
        [data-testid="stMainBlockContainer"] {
            margin-left: auto;
            margin-right: auto;
            max-width: 1400px;
            padding-left: 2rem;
            padding-right: 2rem;
            padding-top: 4.5rem;
        }
        [data-testid="stTopNavLink"], [data-testid="stTopNavDropdownLink"] {
            align-items: center;
            border-bottom: 1px solid transparent;
            color: var(--lab-muted);
            display: flex;
            font-family: 'Inter', sans-serif;
            font-size: 0.875rem;
            font-weight: 500;
            min-height: 44px;
            transition: border-color 0.2s ease, color 0.2s ease;
        }
        [data-testid="stTopNavLink"]:hover, [data-testid="stTopNavDropdownLink"]:hover {
            background: transparent;
            color: var(--lab-primary);
        }
        [data-testid="stTopNavLink"][aria-current="page"] {
            background: transparent;
            border-bottom-color: var(--lab-accent);
            border-radius: 0;
            color: var(--lab-primary);
        }
        [data-testid="stTopNavLink"]:focus-visible, [data-testid="stTopNavDropdownLink"]:focus-visible {
            outline: 2px solid var(--lab-accent);
            outline-offset: 2px;
        }
        [data-testid="stTopNavPopoverBody"] {
            background: var(--lab-surface);
            border: 1px solid var(--lab-border);
            border-radius: var(--lab-radius);
        }
        [data-testid="stSidebar"] {
            background: var(--lab-surface);
            border-right: 1px solid var(--lab-border);
        }
        [data-testid="stMetric"] {
            background: var(--lab-surface);
            border: 1px solid var(--lab-border);
            border-radius: var(--lab-radius);
            padding: 16px;
        }
        [data-testid="stMetricValue"], [data-testid="stDataFrame"] {
            font-variant-numeric: tabular-nums;
        }
        [data-testid="stMetricValue"] {
            color: var(--lab-primary);
            font-weight: 600;
        }
        [data-testid="stMainBlockContainer"] h3 {
            border-left: 3px solid var(--lab-highlight);
            padding-left: 0.65rem;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--lab-border);
            border-radius: var(--lab-radius);
        }
        .lab-kicker {
            color: var(--lab-accent);
            font: 600 0.75rem/1.4 'Geist', sans-serif;
            letter-spacing: 0.12em;
            margin-bottom: 0.35rem;
            text-transform: uppercase;
        }
        .lab-subtitle {
            color: var(--lab-muted);
            font-size: 1rem;
            line-height: 1.6;
            margin: -0.35rem 0 1.4rem;
            max-width: 76ch;
        }
        .lab-status {
            border: 1px solid var(--lab-border);
            border-radius: 999px;
            color: var(--lab-muted);
            display: inline-block;
            font: 600 0.72rem/1 'Geist', sans-serif;
            margin-bottom: 0.8rem;
            padding: 0.42rem 0.62rem;
            text-transform: uppercase;
        }
        .lab-status.connected { border-color: #4993f3; color: #83b5f7; }
        .lab-status.awaiting { border-color: #7d6828; color: #fcd250; }
        .lab-valuation {
            background: var(--lab-surface);
            border: 1px solid var(--lab-border);
            border-radius: var(--lab-radius);
            display: grid;
            grid-template-columns: minmax(240px, 1.15fr) minmax(320px, 1fr);
            margin: 0.5rem 0 2rem;
            overflow: hidden;
        }
        .lab-valuation-primary {
            border-right: 1px solid var(--lab-border);
            padding: 1.5rem;
        }
        .lab-eyebrow {
            color: var(--lab-highlight);
            font: 600 0.72rem/1.4 'Geist', sans-serif;
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }
        .lab-price {
            color: var(--lab-primary);
            font: 600 clamp(2.25rem, 5vw, 3.6rem)/1.05 'Geist', sans-serif;
            font-variant-numeric: tabular-nums;
            letter-spacing: -0.04em;
            margin: 0.45rem 0 0.6rem;
        }
        .lab-price span {
            color: var(--lab-highlight);
            font-size: 0.95rem;
            font-weight: 500;
            letter-spacing: 0;
        }
        .lab-valuation-context {
            color: var(--lab-muted);
            font-size: 0.875rem;
            line-height: 1.5;
        }
        .lab-valuation-details {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .lab-valuation-detail {
            border-bottom: 1px solid var(--lab-border);
            padding: 1rem 1.25rem;
        }
        .lab-valuation-detail:nth-child(odd) { border-right: 1px solid var(--lab-border); }
        .lab-valuation-detail:nth-last-child(-n + 2) { border-bottom: 0; }
        .lab-valuation-detail span,
        .lab-greek span {
            color: var(--lab-muted);
            display: block;
            font-size: 0.75rem;
            font-weight: 500;
            margin-bottom: 0.35rem;
        }
        .lab-valuation-detail strong,
        .lab-greek strong {
            color: var(--lab-primary);
            display: block;
            font-family: 'Geist', sans-serif;
            font-variant-numeric: tabular-nums;
            font-weight: 600;
        }
        .lab-greeks {
            display: grid;
            gap: 1px;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            margin: 0.75rem 0 2rem;
            overflow: hidden;
            background: var(--lab-border);
            border: 1px solid var(--lab-border);
            border-radius: var(--lab-radius);
        }
        .lab-greek {
            background: var(--lab-surface);
            min-width: 0;
            padding: 1rem;
        }
        .lab-greek strong { font-size: 1.25rem; }
        .lab-greek p {
            color: var(--lab-muted);
            font-size: 0.75rem;
            line-height: 1.45;
            margin: 0.45rem 0 0;
        }
        code, .stCodeBlock { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
        @media (max-width: 900px) {
            .lab-valuation { grid-template-columns: 1fr; }
            .lab-valuation-primary { border-bottom: 1px solid var(--lab-border); border-right: 0; }
            .lab-greeks { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
        @media (max-width: 640px) {
            [data-testid="stMainBlockContainer"] { padding-left: 1rem; padding-right: 1rem; padding-top: 4rem; }
            [data-testid="stMetric"] { padding: 10px 12px; }
            .lab-valuation-details { grid-template-columns: 1fr; }
            .lab-valuation-detail,
            .lab-valuation-detail:nth-child(odd),
            .lab-valuation-detail:nth-last-child(-n + 2) {
                border-bottom: 1px solid var(--lab-border);
                border-right: 0;
            }
            .lab-valuation-detail:last-child { border-bottom: 0; }
            .lab-greeks { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .lab-greek:last-child { grid-column: span 2; }
        }
        @media (prefers-reduced-motion: reduce) {
            * { scroll-behavior: auto !important; transition: none !important; animation: none !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_intro(title: str, subtitle: str, status: str | None = None) -> None:
    st.markdown('<div class="lab-kicker">Icelandic Options Lab</div>', unsafe_allow_html=True)
    st.title(title)
    if status:
        css_class = "connected" if status == "Connected" else "awaiting"
        st.markdown(
            f'<span class="lab-status {css_class}">{escape(status)}</span>',
            unsafe_allow_html=True,
        )
    st.markdown(f'<p class="lab-subtitle">{escape(subtitle)}</p>', unsafe_allow_html=True)


def empty_state(title: str, message: str) -> None:
    with st.container(border=True):
        st.subheader(title)
        st.info(message)


def metric_row(metrics: list[tuple[str, str, str | None]]) -> None:
    for column, (label, value, help_text) in zip(st.columns(len(metrics)), metrics):
        column.metric(label, value, help=help_text)


def price_function(option_type: str):
    if option_type == "call":
        return call_option_price
    if option_type == "put":
        return put_option_price
    raise ValueError("option_type must be 'call' or 'put'")


def price_and_greeks(
    option_type: str,
    spot: float | np.ndarray,
    strike: float,
    maturity: float | np.ndarray,
    volatility: float | np.ndarray,
    rate: float,
) -> dict[str, float | np.ndarray]:
    """Call the existing model functions without adding pricing logic."""
    arguments = {
        "S": spot,
        "K": strike,
        "T": maturity,
        "t": 0.0,
        "volatility": volatility,
        "r": rate,
    }
    return {
        "Price": price_function(option_type)(**arguments),
        "Delta": delta(option=option_type, **arguments),
        "Gamma": gamma(**arguments),
        "Vega": vega(**arguments),
        "Theta": theta(option=option_type, **arguments),
        "Rho": rho(option=option_type, **arguments),
    }


def spot_sensitivity_frame(
    option_type: str,
    spot: float,
    strike: float,
    volatility: float,
    maturity: float,
    rate: float,
    points: int = 81,
    width: float = 0.5,
) -> pd.DataFrame:
    spots = np.linspace(max(0.01, spot * (1 - width)), spot * (1 + width), points)
    values = price_and_greeks(option_type, spots, strike, maturity, volatility, rate)
    values["Vega"] = values["Vega"] / 100
    values["Theta"] = values["Theta"] / 365
    values["Rho"] = values["Rho"] / 100
    return pd.DataFrame({"Spot": spots, **values})


def line_figure(
    data: pd.DataFrame,
    x: str,
    series: list[str],
    title: str,
    x_title: str,
    y_title: str,
) -> go.Figure:
    figure = go.Figure()
    for index, column in enumerate(series):
        figure.add_trace(
            go.Scatter(
                x=data[x],
                y=data[column],
                mode="lines",
                name=column,
                line={"color": LINE_COLORS[index % len(LINE_COLORS)], "width": 2},
                hovertemplate=f"{x}: %{{x:,.4f}}<br>{column}: %{{y:,.6f}}<extra></extra>",
            )
        )
    return style_figure(figure, title, x_title, y_title)


def heatmap_figure(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    title: str,
    x_title: str,
    y_title: str,
    value_title: str,
) -> go.Figure:
    figure = go.Figure(
        go.Heatmap(
            x=x,
            y=y,
            z=z,
            colorscale="Cividis",
            colorbar={
                "title": {"text": value_title, "side": "top", "font": {"size": 13}},
                "tickfont": {"size": 13},
                "ticks": "outside",
                "ticklen": 5,
                "thickness": 36,
                "len": 0.92,
                "x": 0.87,
                "xanchor": "left",
                "outlinewidth": 0,
            },
            hovertemplate=(
                f"{x_title}: %{{x:,.4f}}<br>{y_title}: %{{y:,.4f}}"
                f"<br>{value_title}: %{{z:,.6f}}<extra></extra>"
            ),
        )
    )
    figure = style_figure(figure, title, x_title, y_title)
    figure.update_xaxes(domain=[0.0, 0.82])
    return figure


def style_figure(figure: go.Figure, title: str, x_title: str, y_title: str) -> go.Figure:
    figure.update_layout(
        title={"text": title, "x": 0.01, "xanchor": "left", "font": {"family": "Geist, sans-serif"}},
        xaxis_title=x_title,
        yaxis_title=y_title,
        template="plotly_dark",
        paper_bgcolor="#101823",
        plot_bgcolor="#101823",
        font={"color": "#CED5DE", "family": "Inter, sans-serif"},
        hoverlabel={"font_family": "Inter, sans-serif"},
        legend={"orientation": "h", "y": 1.08, "x": 0},
        margin={"l": 48, "r": 24, "t": 72, "b": 48},
        height=390,
    )
    figure.update_xaxes(gridcolor="#2B3B50", zerolinecolor="#61728A")
    figure.update_yaxes(gridcolor="#2B3B50", zerolinecolor="#61728A")
    return figure


def show_plot(figure: go.Figure) -> None:
    st.plotly_chart(figure, width="stretch", config=PLOT_CONFIG)


@st.cache_data(ttl=900, show_spinner=False)
def load_stock_inputs(ticker: str, lookback_days: int, as_of_date: date) -> tuple[float, float]:
    stock = StockData(ticker)
    return stock.get_current_stock_price(as_of_date), stock.get_volatility(lookback_days, as_of_date)


@st.cache_data(ttl=21_600, show_spinner=False)
def load_risk_free_rate(start_date: date, end_date: date) -> float:
    return float(RiskFreeRate(start_date, end_date))
