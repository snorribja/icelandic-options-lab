import pandas as pd
import streamlit as st

from ui.dashboard import configure_page, page_intro
from ui.renderers import render_monte_carlo_results


configure_page("Monte Carlo Research")
page_intro(
    "Monte Carlo Research",
    "Configure a future simulation batch and render engine-supplied paths, distributions, and precomputed statistics.",
    "Awaiting engine",
)

with st.sidebar:
    st.header("Batch configuration")
    simulation_count = st.number_input("Simulation count", min_value=1, max_value=1_000_000, value=10_000, step=1_000)
    realized_volatility = st.slider("Realized volatility (annualized %)", 1.0, 150.0, 25.0, 0.5)
    hedge_frequencies = st.multiselect(
        "Hedge frequencies",
        ["Every step", "Every 2 steps", "Every 5 steps", "Every 21 steps"],
        default=["Every step", "Every 5 steps", "Every 21 steps"],
    )
    transaction_costs = st.number_input("Transaction costs (% of traded notional)", min_value=0.0, value=0.0, step=0.01)
    seed = st.number_input("Random seed", min_value=0, max_value=2_147_483_647, value=202, step=1)

st.subheader("Configured batch")
st.dataframe(
    pd.DataFrame(
        {
            "Input": ["Simulation count", "Realized volatility", "Hedge frequencies", "Transaction costs", "Seed"],
            "Value": [
                f"{simulation_count:,}",
                f"{realized_volatility:.2f}%",
                ", ".join(hedge_frequencies) or "None selected",
                f"{transaction_costs:.3f}%",
                f"{seed}",
            ],
        }
    ),
    width="stretch",
    hide_index=True,
)

results_df = None
summary_statistics = None
# TODO(user): pass the Monte Carlo engine's results DataFrame and precomputed summary statistics here.
render_monte_carlo_results(results_df, summary_statistics)
