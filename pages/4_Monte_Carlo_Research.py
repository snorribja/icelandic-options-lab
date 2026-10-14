from datetime import date, timedelta

import pandas as pd
import streamlit as st

from options_lab.config import ICELANDIC_STOCKS
from options_lab.simulation import MonteCarlo
from ui.charts import render_monte_carlo_dashboard
from ui.components import configure_page, empty_state, page_intro


configure_page("Monte Carlo Research")
page_intro(
    "Monte Carlo Research",
    "Run GBM simulations and compare discrete delta-hedging errors across rebalancing frequencies.",
)

frequency_to_days = {
    "Every day": 1,
    "Every 2 days": 2,
    "Every 5 days": 5,
    "Every 21 days": 21,
}

with st.sidebar:
    st.header("Simulation configuration")
    ticker = st.selectbox(
        "Icelandic ticker",
        options=list(ICELANDIC_STOCKS),
        format_func=lambda value: f"{value} — {ICELANDIC_STOCKS[value]}",
    )
    option_type = st.radio("Option type", ["call", "put"], horizontal=True, format_func=str.title)
    strike_price = st.number_input("Strike price (ISK)", min_value=0.01, value=100.0, step=1.0)
    simulation_count = st.number_input(
        "Simulation count",
        min_value=1,
        max_value=200,
        value=10,
        step=1,
        help="Keep this small until rate lookup is cached; the current hedge engine resolves the rate for each hedge run.",
    )
    horizon_days = st.number_input(
        "Simulation horizon (calendar days)",
        min_value=1,
        max_value=3_650,
        value=365,
        step=30,
    )
    hedge_frequencies = st.multiselect(
        "Hedge frequencies",
        list(frequency_to_days),
        default=["Every day", "Every 5 days", "Every 21 days"],
    )
    transaction_cost_percentage = st.number_input(
        "Transaction costs (%)",
        min_value=0.0,
        value=0.1,
        step=0.01,
        help="Applied to traded notional at each hedge rebalance.",
    )
    path_count = st.slider("Paths to display", min_value=5, max_value=50, value=25, step=5)
    run_simulation = st.button("Run Monte Carlo", type="primary", width="stretch")

st.subheader("Configured simulation")
st.dataframe(
    pd.DataFrame(
        {
            "Input": ["Ticker", "Option", "Strike", "Simulation count", "Horizon", "Hedge frequencies", "Transaction costs (%)"],
            "Value": [
                ticker,
                option_type.title(),
                f"{strike_price:,.2f} ISK",
                f"{simulation_count:,}",
                f"{horizon_days:,} days",
                ", ".join(hedge_frequencies) or "None selected",
                f"{transaction_cost_percentage:,} %",
            ],
        }
    ),
    width="stretch",
    hide_index=True,
)

if run_simulation:
    if not hedge_frequencies:
        st.error("Select at least one hedge frequency.")
    else:
        try:
            start_date = date.today()
            end_date = start_date + timedelta(days=int(horizon_days))
            with st.status("Preparing Monte Carlo calculation…", expanded=True) as calculation_status:
                st.write("Loading cached market data.")
                simulation = MonteCarlo(
                    stock_name=ticker,
                    sims=int(simulation_count),
                    hedge_freq=[frequency_to_days[value] for value in hedge_frequencies],
                    option_type=option_type,
                    strike_price=float(strike_price),
                    start_date=start_date,
                    end_date=end_date,
                    transaction_cost_per=transaction_cost_percentage/100,
                    option_quantity=1.0,
                )
                st.write(f"Generated {int(simulation_count):,} simulated price paths.")
                st.write("Calculating delta hedges and transaction costs.")
                results_df, summary_statistics = simulation.run()
                display_paths = simulation.stock_price_matrix
                st.write("Organizing results for the dashboard.")
                calculation_status.update(label="Monte Carlo calculation complete", state="complete", expanded=False)
            st.session_state["monte_carlo_result"] = (results_df, summary_statistics, display_paths, start_date, int(path_count))
        except Exception as exc:
            if "calculation_status" in locals():
                calculation_status.update(label="Monte Carlo calculation failed", state="error", expanded=True)
            st.error(f"The Monte Carlo run could not be completed: {exc}")

result = st.session_state.get("monte_carlo_result")
if result and len(result) == 5:
    results_df, summary_statistics, display_paths, start_date, path_count = result
else:
    results_df = summary_statistics = display_paths = start_date = None
    path_count = 25

if results_df is None:
    empty_state("Ready to run", "Configure the simulation and select Run Monte Carlo.")

render_monte_carlo_dashboard(
    results_df,
    summary_statistics,
    price_matrix=display_paths,
    start_date=start_date,
    path_count=path_count,
)
