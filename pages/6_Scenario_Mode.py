import numpy as np
import streamlit as st

from options_lab.analysis import price_and_greeks, spot_sensitivity_frame
from ui.charts import line_figure, show_plot
from ui.components import configure_page, metric_row, page_intro


configure_page("Scenario Mode")
page_intro(
    "Scenario Mode",
    "Move the assumptions and inspect immediate output from the existing Black–Scholes and Greek functions.",
)

with st.sidebar:
    st.header("Live scenario")
    option_type = st.radio("Option type", ["call", "put"], horizontal=True, format_func=str.title)
    spot = st.slider("Spot (ISK)", 1.0, 1_000.0, 100.0, 1.0)
    strike = st.slider("Strike (ISK)", 1.0, 1_000.0, 100.0, 1.0)
    volatility_pct = st.slider("Volatility (annualized %)", 1.0, 150.0, 25.0, 0.5)
    rate_pct = st.slider("Interest rate (continuous annualized %)", -10.0, 50.0, 8.0, 0.1)
    maturity = st.slider("Time to expiration (years)", 0.01, 10.0, 1.0, 0.01)
    st.number_input("Dividend yield (%) — unsupported", value=0.0, disabled=True)

values = price_and_greeks(option_type, spot, strike, maturity, volatility_pct / 100, rate_pct / 100)
if not all(np.isfinite(value) for value in values.values()):
    st.error("The existing model returned a non-finite value for this scenario. Adjust the inputs.")
    st.stop()

metric_row(
    [
        ("Price", f"{values['Price']:,.2f} ISK", "Existing Black–Scholes pricer"),
        ("Delta", f"{values['Delta']:,.4f}", "Per 1 ISK spot change"),
        ("Gamma", f"{values['Gamma']:,.6f}", "Per 1 ISK spot change"),
    ]
)
metric_row(
    [
        ("Vega", f"{values['Vega'] / 100:,.4f}", "ISK per one percentage-point volatility change"),
        ("Theta", f"{values['Theta'] / 365:,.4f}", "ISK per calendar day"),
        ("Rho", f"{values['Rho'] / 100:,.4f}", "ISK per one percentage-point rate change"),
    ]
)

nearby = spot_sensitivity_frame(option_type, spot, strike, volatility_pct / 100, maturity, rate_pct / 100, points=61, width=0.25)
charts = [
    ("Price", "Nearby option price", "Option value (ISK)"),
    ("Delta", "Nearby Delta", "Delta"),
    ("Gamma", "Nearby Gamma", "Gamma (per ISK)"),
    ("Vega", "Nearby Vega", "Vega (ISK per volatility percentage point)"),
    ("Theta", "Nearby Theta", "Theta (ISK per calendar day)"),
    ("Rho", "Nearby Rho", "Rho (ISK per rate percentage point)"),
]
for left, right in zip(charts[::2], charts[1::2]):
    columns = st.columns(2)
    for container, (series, title, unit) in zip(columns, (left, right)):
        with container:
            show_plot(line_figure(nearby, "Spot", [series], title, "Spot (ISK)", unit))

with st.expander("Nearby sensitivity data table"):
    st.dataframe(nearby, width="stretch", hide_index=True)
