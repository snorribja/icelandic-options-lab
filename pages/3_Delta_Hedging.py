import pandas as pd
import streamlit as st

from ui.dashboard import configure_page, page_intro
from ui.renderers import render_hedging_results


configure_page("Delta Hedging")
page_intro(
    "Delta Hedging",
    "Configure a discrete-hedging scenario. This page is a renderer and does not simulate paths or manage a hedge account.",
    "Awaiting engine",
)

with st.sidebar:
    st.header("Hedging scenario")
    initial_spot = st.number_input("Initial spot (ISK)", min_value=0.01, value=100.0, step=1.0)
    strike = st.number_input("Strike (ISK)", min_value=0.01, value=100.0, step=1.0)
    option_type = st.radio("Option type", ["call", "put"], horizontal=True, format_func=str.title)
    maturity = st.slider("Maturity (years)", 0.01, 10.0, 1.0, 0.01)
    pricing_volatility = st.slider("Pricing volatility (annualized %)", 1.0, 150.0, 25.0, 0.5)
    realized_volatility = st.slider("Realized volatility (annualized %)", 1.0, 150.0, 25.0, 0.5)
    interest_rate = st.slider("Interest rate (continuous annualized %)", -10.0, 50.0, 8.0, 0.1)
    simulation_steps = st.number_input("Simulation steps", min_value=2, max_value=100_000, value=252, step=1)
    hedge_frequency = st.selectbox("Hedge frequency", ["Every step", "Every 2 steps", "Every 5 steps", "Every 21 steps"])
    transaction_costs = st.number_input("Transaction costs (% of traded notional)", min_value=0.0, value=0.0, step=0.01)

st.subheader("Configured scenario")
st.dataframe(
    pd.DataFrame(
        {
            "Input": [
                "Initial spot",
                "Strike",
                "Option type",
                "Maturity",
                "Pricing volatility",
                "Realized volatility",
                "Interest rate",
                "Simulation steps",
                "Hedge frequency",
                "Transaction costs",
            ],
            "Value": [
                f"{initial_spot:,.2f} ISK",
                f"{strike:,.2f} ISK",
                option_type.title(),
                f"{maturity:.2f} years",
                f"{pricing_volatility:.2f}%",
                f"{realized_volatility:.2f}%",
                f"{interest_rate:.2f}%",
                f"{simulation_steps:,}",
                hedge_frequency,
                f"{transaction_costs:.3f}%",
            ],
        }
    ),
    width="stretch",
    hide_index=True,
)

path_df = None
summary = None
# TODO(user): pass output from the delta-hedging engine here as path_df and summary.
render_hedging_results(path_df, summary)
