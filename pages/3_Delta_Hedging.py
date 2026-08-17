from datetime import date, timedelta

import pandas as pd
import streamlit as st

from global_vars import ICELANDIC_STOCKS
from hedging import HedgeEngine
from ui.dashboard import configure_page, empty_state, page_intro
from ui.renderers import render_hedging_results


configure_page("Delta Hedging")
page_intro(
    "Delta Hedging",
    "Run the current hedge engine against an observed Icelandic stock-price path.",
)

today = date.today()
with st.sidebar:
    st.header("Historical hedge")
    with st.form("delta_hedging_form"):
        ticker = st.selectbox(
            "Icelandic ticker",
            options=list(ICELANDIC_STOCKS),
            format_func=lambda value: f"{value} — {ICELANDIC_STOCKS[value]}",
        )
        option_type = st.radio("Option type", ["call", "put"], horizontal=True, format_func=str.title)
        strike = st.number_input("Strike (ISK)", min_value=0.01, value=1_700.0, step=1.0)
        start_date = st.date_input(
            "Start date",
            value=today - timedelta(days=365),
            min_value=today - timedelta(days=3650),
            max_value=today - timedelta(days=1),
        )
        end_date = st.date_input(
            "Expiration date",
            value=today,
            min_value=today - timedelta(days=3649),
            max_value=today,
        )
        option_quantity = st.number_input(
            "Option quantity",
            min_value=1,
            value=100,
            step=1,
            help="In the current engine, one option represents one underlying share.",
        )
        hedge_interval_days = st.number_input(
            "Days between hedges",
            min_value=1,
            max_value=365,
            value=7,
            step=1,
            help="Calendar days. Weekend and market-closure prices use the previous available trading day.",
        )
        st.number_input(
            "Transaction costs (%) — unsupported",
            value=0.0,
            disabled=True,
            help="The current hedge engine reports zero transaction costs until its cost accounting is implemented.",
        )
        run_hedge = st.form_submit_button("Run historical hedge", type="primary", width="stretch")

st.subheader("Configured scenario")
st.caption("The engine resolves stock prices, historical volatility, and the Icelandic rate from its existing data sources.")
st.dataframe(
    pd.DataFrame(
        [
            ("Ticker", ticker, "User selection"),
            ("Option", option_type.title(), "European call or put"),
            ("Strike", f"{strike:,.2f} ISK", "User input"),
            ("Start date", f"{start_date:%d %b %Y}", "Historical path start"),
            ("Expiration", f"{end_date:%d %b %Y}", "Historical path end and option expiry"),
            ("Option quantity", f"{option_quantity:,}", "One option represents one underlying share"),
            ("Hedge interval", f"Every {hedge_interval_days} calendar days", "Final interval is shortened to reach expiry"),
            ("Stock path", "Automatic", "Yahoo Finance adjusted close"),
            ("Pricing volatility", "Automatic", "60-calendar-day historical estimate at each hedge date"),
            ("Risk-free rate", "Automatic", "Icelandic rate resolved once for the contract term"),
            ("Transaction costs", "0.00 ISK", "Not implemented in the current engine"),
        ],
        columns=["Input", "Value", "Source / convention"],
    ),
    width="stretch",
    hide_index=True,
)

if run_hedge:
    st.session_state.pop("delta_hedging_result", None)
    if end_date <= start_date:
        st.error("Expiration must be after the start date. Adjust the dates and run the hedge again.")
    else:
        try:
            with st.spinner(f"Loading market data and hedging {ticker}…"):
                engine = HedgeEngine(
                    stock_name=ticker,
                    option_type=option_type,
                    strike_price=float(strike),
                    start_date=start_date,
                    end_date=end_date,
                    current_date=start_date,
                    option_quantity=float(option_quantity),
                )
                path_df, summary = engine.hedge_simulation(int(hedge_interval_days))
            st.session_state["delta_hedging_result"] = (path_df, summary)
        except Exception as exc:
            st.error(
                f"The hedge could not be run: {exc}. Check the dates and ticker, then retry when the market-data sources are available."
            )

if result := st.session_state.get("delta_hedging_result"):
    render_hedging_results(*result)
else:
    empty_state(
        "Ready to run",
        "Configure the historical contract in the sidebar and select Run historical hedge. No results are generated until the engine completes.",
    )
