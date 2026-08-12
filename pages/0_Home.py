import pandas as pd
import streamlit as st

from ui.dashboard import configure_page, page_intro


configure_page("Home")
page_intro(
    "Research dashboard",
    "A compact interface around the option-pricing and market-data code that exists in this repository. Research engines remain deliberately outside the dashboard layer.",
)

st.subheader("Research objective")
st.write(
    "Explore Icelandic equity-option pricing, sensitivities, and—once the relevant engines are connected—"
    "the behavior of discrete hedging errors under practical market assumptions."
)

connected, awaiting = st.columns(2)
with connected:
    with st.container(border=True):
        st.markdown("#### Currently connected")
        st.markdown(
            "- Black–Scholes call and put pricing\n"
            "- Delta, Gamma, Vega, Theta, and Rho\n"
            "- Yahoo Finance spot/history and historical volatility\n"
            "- Icelandic risk-free-rate retrieval"
        )
with awaiting:
    with st.container(border=True):
        st.markdown("#### Awaiting your engines")
        st.markdown(
            "- Path simulation and discrete delta hedging\n"
            "- Cash-account and transaction-cost accounting\n"
            "- Monte Carlo statistics\n"
            "- Research experiments and interpretations"
        )

st.subheader("Conventions")
st.dataframe(
    pd.DataFrame(
        [
            ("Price", "ISK"),
            ("Rate input", "Continuously compounded annualized %"),
            ("Volatility input", "Annualized %"),
            ("Time", "Calendar years; 365-day conversion"),
            ("Theta", "ISK per calendar day"),
            ("Vega", "ISK per one percentage-point volatility change"),
            ("Rho", "ISK per one percentage-point rate change"),
        ],
        columns=["Measure", "Dashboard convention"],
    ),
    width="stretch",
    hide_index=True,
)
st.caption("Dividend yield is not supported by the current pricing model. No research result is fabricated by this interface.")
