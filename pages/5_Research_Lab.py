import streamlit as st

from ui.charts import render_research_experiment
from ui.components import configure_page, page_intro


configure_page("Research Lab")
page_intro(
    "Research Lab",
    "Five reserved experiment panels. Controls capture assumptions; calculations, statistics, and interpretations remain owned by your research code.",
    "Awaiting engines",
)

frequency_tab, volatility_tab, costs_tab, moneyness_tab, maturity_tab = st.tabs(
    ["Hedging frequency", "Volatility misspecification", "Transaction costs", "Moneyness", "Time to maturity"]
)

with frequency_tab:
    st.markdown("#### Hedging frequency")
    st.write("**Research question:** How does rebalancing frequency affect the distribution of terminal hedging error?")
    first, second, third = st.columns(3)
    first.multiselect(
        "Frequencies to compare",
        ["Every step", "Every 2 steps", "Every 5 steps", "Every 21 steps"],
        default=["Every step", "Every 5 steps", "Every 21 steps"],
        key="lab_frequency_levels",
    )
    second.number_input("Simulations per frequency", min_value=1, value=10_000, step=1_000, key="lab_frequency_sims")
    third.number_input("Transaction costs (%)", min_value=0.0, value=0.0, step=0.01, key="lab_frequency_costs")
    frequency_results = frequency_statistics = frequency_interpretation = None
    # TODO(user): pass hedging-frequency experiment outputs and interpretation here.
    render_research_experiment(
        frequency_results,
        frequency_statistics,
        frequency_interpretation,
        x="hedge_frequency",
        y="error",
        chart_title="Hedging error by frequency",
    )

with volatility_tab:
    st.markdown("#### Volatility misspecification")
    st.write("**Research question:** How does a gap between pricing and realized volatility affect hedging error?")
    first, second, third = st.columns(3)
    first.slider("Pricing volatility (%)", 1.0, 150.0, 25.0, 0.5, key="lab_pricing_vol")
    second.multiselect(
        "Realized volatility levels (%)", [10, 15, 20, 25, 30, 40, 50, 75], default=[15, 25, 40], key="lab_realized_vols"
    )
    third.number_input("Simulations per level", min_value=1, value=10_000, step=1_000, key="lab_vol_sims")
    volatility_results = volatility_statistics = volatility_interpretation = None
    # TODO(user): pass volatility-misspecification experiment outputs and interpretation here.
    render_research_experiment(
        volatility_results,
        volatility_statistics,
        volatility_interpretation,
        x="volatility_gap",
        y="error",
        chart_title="Hedging error by volatility gap",
    )

with costs_tab:
    st.markdown("#### Transaction costs")
    st.write("**Research question:** How does rebalancing interact with proportional transaction costs?")
    first, second, third = st.columns(3)
    first.multiselect(
        "Cost levels (%)", [0.0, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0], default=[0.0, 0.1, 0.5], key="lab_cost_levels"
    )
    second.selectbox(
        "Hedge frequency", ["Every step", "Every 2 steps", "Every 5 steps", "Every 21 steps"], key="lab_cost_frequency"
    )
    third.number_input("Simulations per level", min_value=1, value=10_000, step=1_000, key="lab_cost_sims")
    cost_results = cost_statistics = cost_interpretation = None
    # TODO(user): pass transaction-cost experiment outputs and interpretation here.
    render_research_experiment(
        cost_results,
        cost_statistics,
        cost_interpretation,
        x="transaction_cost_rate",
        y="error",
        chart_title="Hedging error by transaction-cost rate",
    )

with moneyness_tab:
    st.markdown("#### Moneyness")
    st.write("**Research question:** How does initial option moneyness affect the terminal hedging-error distribution?")
    first, second, third = st.columns(3)
    first.number_input("Initial spot (ISK)", min_value=0.01, value=100.0, step=1.0, key="lab_moneyness_spot")
    second.multiselect(
        "Strike / spot ratios", [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3], default=[0.8, 1.0, 1.2], key="lab_moneyness_levels"
    )
    third.number_input("Simulations per ratio", min_value=1, value=10_000, step=1_000, key="lab_moneyness_sims")
    moneyness_results = moneyness_statistics = moneyness_interpretation = None
    # TODO(user): pass moneyness experiment outputs and interpretation here.
    render_research_experiment(
        moneyness_results,
        moneyness_statistics,
        moneyness_interpretation,
        x="moneyness",
        y="error",
        chart_title="Hedging error by initial moneyness",
    )

with maturity_tab:
    st.markdown("#### Time to maturity")
    st.write("**Research question:** How does the initial time horizon affect discrete hedging error?")
    first, second, third = st.columns(3)
    first.multiselect(
        "Maturities (years)", [1 / 12, 0.25, 0.5, 1.0, 2.0, 5.0], default=[0.25, 0.5, 1.0], key="lab_maturities"
    )
    second.selectbox(
        "Hedge frequency", ["Every step", "Every 2 steps", "Every 5 steps", "Every 21 steps"], key="lab_maturity_frequency"
    )
    third.number_input("Simulations per maturity", min_value=1, value=10_000, step=1_000, key="lab_maturity_sims")
    maturity_results = maturity_statistics = maturity_interpretation = None
    # TODO(user): pass time-to-maturity experiment outputs and interpretation here.
    render_research_experiment(
        maturity_results,
        maturity_statistics,
        maturity_interpretation,
        x="maturity_years",
        y="error",
        chart_title="Hedging error by time to maturity",
    )
