from datetime import date, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from options_lab.analysis import price_and_greeks
from options_lab.config import ICELANDIC_STOCKS
from options_lab.option_info import OptionInfo
from ui.charts import COLORS, show_plot, style_figure
from ui.components import (
    configure_page,
    empty_state,
    load_risk_free_rate,
    load_stock_inputs,
    page_intro,
)


configure_page("Option Pricer")
page_intro(
    "Option Pricer",
    "Value a European call or put with the existing Black–Scholes model and Icelandic market inputs.",
)

today = date.today()
with st.sidebar:
    st.header("Contract")
    ticker = st.selectbox(
        "Icelandic ticker",
        options=list(ICELANDIC_STOCKS),
        format_func=lambda value: f"{value} — {ICELANDIC_STOCKS[value]}",
    )
    option_type = st.radio("Option type", ["call", "put"], horizontal=True, format_func=str.title)
    strike_slot = st.empty()
    expiration = st.date_input(
        "Expiration date",
        value=today + timedelta(days=365),
        min_value=today + timedelta(days=1),
        max_value=today + timedelta(days=3650),
    )
    lookback = st.select_slider("Volatility lookback (calendar days)", [30, 60, 90, 180, 252], value=60)

    st.divider()
    st.header("Market inputs")
    automatic_spot = st.checkbox("Automatic spot price", value=True)
    manual_spot = st.number_input("Manual spot override (ISK)", min_value=0.01, value=100.0, disabled=automatic_spot)
    automatic_rate = st.checkbox("Automatic Icelandic risk-free rate", value=True)
    manual_rate_pct = st.number_input(
        "Manual rate override (%)", min_value=-20.0, max_value=100.0, value=8.0, step=0.1, disabled=automatic_rate
    )
    automatic_volatility = st.checkbox("Automatic historical volatility", value=True)
    manual_volatility_pct = st.number_input(
        "Manual volatility override (%)", min_value=0.01, max_value=500.0, value=25.0, step=0.5, disabled=automatic_volatility
    )
    st.number_input(
        "Dividend yield (%) — unsupported",
        value=0.0,
        disabled=True,
        help="The current Black–Scholes implementation has no dividend-yield input.",
    )

spot = None if automatic_spot else float(manual_spot)
volatility = None if automatic_volatility else float(manual_volatility_pct) / 100
rate = None if automatic_rate else float(manual_rate_pct) / 100
errors: list[str] = []

if automatic_spot or automatic_volatility:
    try:
        with st.spinner(f"Loading Yahoo Finance data for {ticker}…"):
            loaded_spot, loaded_volatility = load_stock_inputs(ticker, lookback, today)
        if automatic_spot:
            spot = loaded_spot
        if automatic_volatility:
            volatility = loaded_volatility
    except Exception as exc:
        errors.append(
            f"Yahoo Finance inputs could not be loaded ({exc}). Disable the affected automatic controls and enter manual values."
        )

strike = None
if spot is not None and spot > 0:
    strike_basis = (ticker, round(float(spot), 8))
    if st.session_state.get("option_pricer_strike_basis") != strike_basis:
        st.session_state["option_pricer_strike"] = round(float(spot) * 1.05, 2)
        st.session_state["option_pricer_strike_basis"] = strike_basis
    with strike_slot:
        strike = st.number_input(
            "Strike (ISK)",
            min_value=0.01,
            step=1.0,
            format="%.2f",
            key="option_pricer_strike",
            help="Defaults to 105% of the starting stock price and remains editable.",
        )

if automatic_rate:
    try:
        with st.spinner("Loading the Icelandic risk-free rate…"):
            rate = load_risk_free_rate(today, expiration)
    except Exception as exc:
        errors.append(
            f"The Icelandic rate could not be loaded ({exc}). Disable automatic rate and enter a manual continuously compounded rate."
        )

if errors:
    for message in errors:
        st.error(message)
    empty_state("Manual recovery available", "Use the sidebar overrides to continue without the unavailable network source.")
    st.stop()

if spot is None or strike is None or volatility is None or rate is None or spot <= 0 or volatility <= 0:
    st.error("Spot and volatility must be positive, and all market inputs must be available.")
    st.stop()

maturity = (expiration - today).days / 365
try:
    option_value = OptionInfo().price(
        option_type=option_type,
        stock_price=spot,
        strike_price=strike,
        volatility=volatility,
        rate=rate,
        start_date=today,
        end_date=expiration,
        current_date=today,
    )
    greeks = price_and_greeks(option_type, spot, strike, maturity, volatility, rate)
    if not all(np.isfinite(value) for value in [option_value, *greeks.values()]):
        raise ValueError("the pricing backend returned a non-finite value")
except Exception as exc:
    st.error(f"The existing pricing model could not evaluate these inputs: {exc}. Review the contract and market inputs.")
    st.stop()

intrinsic = max(spot - strike, 0.0) if option_type == "call" else max(strike - spot, 0.0)
time_value = option_value - intrinsic

st.markdown(
    f"""
    <section class="lab-valuation" aria-label="Option valuation summary">
        <div class="lab-valuation-primary">
            <div class="lab-eyebrow">Black–Scholes model value</div>
            <div class="lab-price">{option_value:,.2f}<span> ISK</span></div>
            <div class="lab-valuation-context">
                European {option_type} · {ticker} · expires {expiration:%d %b %Y}
            </div>
        </div>
        <div class="lab-valuation-details">
            <div class="lab-valuation-detail"><span>Intrinsic value</span><strong>{intrinsic:,.2f} ISK</strong></div>
            <div class="lab-valuation-detail"><span>Time value</span><strong>{time_value:,.2f} ISK</strong></div>
            <div class="lab-valuation-detail"><span>Current stock price</span><strong>{spot:,.2f} ISK</strong></div>
            <div class="lab-valuation-detail"><span>Strike price</span><strong>{strike:,.2f} ISK</strong></div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.subheader("Risk sensitivities")
st.caption("Greeks are normalized to practical display units; definitions are shown on each measure.")
st.markdown(
    f"""
    <section class="lab-greeks" aria-label="Option risk sensitivities">
        <div class="lab-greek"><span>Delta</span><strong>{greeks['Delta']:,.4f}</strong><p>Option value change per 1 ISK stock-price move</p></div>
        <div class="lab-greek"><span>Gamma</span><strong>{greeks['Gamma']:,.6f}</strong><p>Delta change per 1 ISK stock-price move</p></div>
        <div class="lab-greek"><span>Vega</span><strong>{greeks['Vega'] / 100:,.4f}</strong><p>ISK per 1 percentage-point volatility move</p></div>
        <div class="lab-greek"><span>Theta</span><strong>{greeks['Theta'] / 365:,.4f}</strong><p>ISK per calendar day</p></div>
        <div class="lab-greek"><span>Rho</span><strong>{greeks['Rho'] / 100:,.4f}</strong><p>ISK per 1 percentage-point rate move</p></div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.subheader("Contract inputs")
st.caption("Resolved values and the source or convention applied to each input.")
st.dataframe(
    pd.DataFrame(
        [
            ("Ticker", ticker, "User selection"),
            ("Stock price", f"{spot:,.4f} ISK", "Yahoo Finance adjusted close" if automatic_spot else "Manual override"),
            ("Strike", f"{strike:,.4f} ISK", "User-editable; initialized at 105% of the stock price"),
            ("Volatility", f"{volatility:.2%} annualized", "Historical" if automatic_volatility else "Manual override"),
            ("Risk-free rate", f"{rate:.2%} continuous annualized", "Icelandic rate data" if automatic_rate else "Manual override"),
            ("Maturity", f"{maturity:.4f} years", "Calendar days / 365"),
            ("Dividend yield", "Unsupported", "Current model excludes dividends"),
        ],
        columns=["Input", "Value", "Source / convention"],
    ),
    width="stretch",
    hide_index=True,
)

terminal_spots = np.linspace(max(0.01, min(spot, strike) * 0.4), max(spot, strike) * 1.8, 121)
payoff = np.maximum(terminal_spots - strike, 0) if option_type == "call" else np.maximum(strike - terminal_spots, 0)
profit_loss = payoff - option_value
figure = go.Figure()
figure.add_trace(go.Scatter(x=terminal_spots, y=payoff, name="Payoff", line={"color": COLORS[0], "width": 2}))
figure.add_trace(go.Scatter(x=terminal_spots, y=profit_loss, name="Long P/L", line={"color": COLORS[2], "width": 2}))
figure.add_hline(y=0, line_dash="dash", line_color="#94A3B8", annotation_text="Zero profit / loss")
st.subheader("Payoff at expiration")
st.caption("Stock price at expiration is the market price of the underlying share when the option contract expires.")
show_plot(
    style_figure(
        figure,
        f"Long {option_type}: payoff and profit / loss",
        "Stock price at expiration (ISK)",
        "Value (ISK)",
    )
)

break_even = strike + option_value if option_type == "call" else strike - option_value
reference_points = [
    ("Lower chart range", terminal_spots[0]),
    ("Strike — zero payoff", strike),
    ("Break-even — zero P/L", break_even),
    ("Upper chart range", terminal_spots[-1]),
]
payoff_rows = []
for scenario, stock_price_at_expiration in reference_points:
    if stock_price_at_expiration < 0:
        scenario, stock_price_at_expiration = "Current stock price", spot
    point_payoff = (
        max(stock_price_at_expiration - strike, 0)
        if option_type == "call"
        else max(strike - stock_price_at_expiration, 0)
    )
    payoff_rows.append((scenario, stock_price_at_expiration, point_payoff, point_payoff - option_value))

with st.expander("Four key payoff values"):
    st.dataframe(
        pd.DataFrame(
            payoff_rows,
            columns=["Reference point", "Stock price at expiration", "Payoff", "Long P/L"],
        ),
        column_config={
            "Stock price at expiration": st.column_config.NumberColumn(format="%.2f ISK"),
            "Payoff": st.column_config.NumberColumn(format="%.2f ISK"),
            "Long P/L": st.column_config.NumberColumn(format="%.2f ISK"),
        },
        width="stretch",
        hide_index=True,
    )
