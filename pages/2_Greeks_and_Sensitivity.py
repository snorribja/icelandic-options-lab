import numpy as np
import pandas as pd
import streamlit as st

from options_lab.analysis import price_function, spot_sensitivity_frame
from options_lab.pricing import delta, gamma, vega
from ui.charts import heatmap_figure, line_figure, show_plot
from ui.components import (
    configure_page,
    page_intro,
)


configure_page("Greeks & Sensitivity")
page_intro(
    "Greeks & Sensitivity",
    "Inspect the existing Black–Scholes price and Greek functions across moderate, responsive input grids.",
)

with st.sidebar:
    st.header("Scenario")
    option_type = st.radio("Option type", ["call", "put"], horizontal=True, format_func=str.title)
    spot = st.number_input("Spot (ISK)", min_value=0.01, value=100.0, step=1.0)
    strike = st.number_input("Strike (ISK)", min_value=0.01, value=100.0, step=1.0)
    volatility_pct = st.slider("Volatility (annualized %)", 1.0, 150.0, 25.0, 0.5)
    maturity = st.slider("Maturity (years)", 0.01, 10.0, 1.0, 0.01)
    rate_pct = st.slider("Interest rate (continuous annualized %)", -10.0, 50.0, 8.0, 0.1)
    st.number_input("Dividend yield (%) — unsupported", value=0.0, disabled=True)

volatility = volatility_pct / 100
rate = rate_pct / 100
pricer = price_function(option_type)
spot_data = spot_sensitivity_frame(option_type, spot, strike, volatility, maturity, rate)

spot_tab, alternative_tab, heatmap_tab = st.tabs(["Spot curves", "Volatility & time", "Heatmaps"])

with spot_tab:
    chart_specs = [
        ("Price", "Option price vs spot", "Option value (ISK)"),
        ("Delta", "Delta vs spot", "Delta"),
        ("Gamma", "Gamma vs spot", "Gamma (per ISK)"),
        ("Vega", "Vega vs spot", "Vega (ISK per volatility percentage point)"),
        ("Theta", "Theta vs spot", "Theta (ISK per calendar day)"),
        ("Rho", "Rho vs spot", "Rho (ISK per rate percentage point)"),
    ]
    for left, right in zip(chart_specs[::2], chart_specs[1::2]):
        columns = st.columns(2)
        for container, (column, title, unit) in zip(columns, (left, right)):
            with container:
                show_plot(line_figure(spot_data, "Spot", [column], title, "Spot (ISK)", unit))
    with st.expander("Spot-sensitivity data table"):
        st.dataframe(
            spot_data,
            column_config={
                "Spot": st.column_config.NumberColumn("Spot (ISK)", format="%.2f"),
                "Price": st.column_config.NumberColumn("Price (ISK)", format="%.2f"),
                "Delta": st.column_config.NumberColumn(format="%.4f"),
                "Gamma": st.column_config.NumberColumn(format="%.6g"),
                "Vega": st.column_config.NumberColumn("Vega (ISK / vol. pp)", format="%.4f"),
                "Theta": st.column_config.NumberColumn("Theta (ISK / day)", format="%.4f"),
                "Rho": st.column_config.NumberColumn("Rho (ISK / rate pp)", format="%.4f"),
            },
            width="stretch",
            hide_index=True,
        )

with alternative_tab:
    volatilities = np.linspace(max(0.01, volatility * 0.25), max(volatility * 2, volatility + 0.05), 61)
    maturities = np.linspace(1 / 365, min(10.0, max(maturity * 1.5, maturity + 0.1)), 61)
    volatility_data = pd.DataFrame(
        {"Volatility": volatilities, "Price": pricer(S=spot, K=strike, T=maturity, t=0.0, volatility=volatilities, r=rate)}
    )
    maturity_data = pd.DataFrame(
        {"Maturity": maturities, "Price": pricer(S=spot, K=strike, T=maturities, t=0.0, volatility=volatility, r=rate)}
    )
    first, second = st.columns(2)
    with first:
        show_plot(line_figure(volatility_data, "Volatility", ["Price"], "Option price vs volatility", "Annualized volatility (decimal)", "Option value (ISK)"))
    with second:
        show_plot(line_figure(maturity_data, "Maturity", ["Price"], "Option price vs time to expiration", "Time to expiration (years)", "Option value (ISK)"))
    with st.expander("Volatility and maturity data tables"):
        first, second = st.columns(2)
        first.dataframe(
            volatility_data.assign(Volatility=volatility_data["Volatility"] * 100),
            column_config={
                "Volatility": st.column_config.NumberColumn("Volatility", format="%.2f%%"),
                "Price": st.column_config.NumberColumn("Price (ISK)", format="%.2f"),
            },
            width="stretch",
            hide_index=True,
        )
        second.dataframe(
            maturity_data,
            column_config={
                "Maturity": st.column_config.NumberColumn("Maturity (years)", format="%.3f"),
                "Price": st.column_config.NumberColumn("Price (ISK)", format="%.2f"),
            },
            width="stretch",
            hide_index=True,
        )

with heatmap_tab:
    heat_spots = np.linspace(max(0.01, spot * 0.5), spot * 1.5, 35)
    heat_volatilities = np.linspace(max(0.01, volatility * 0.3), max(volatility * 1.8, volatility + 0.05), 30)
    heat_maturities = np.linspace(max(1 / 365, maturity * 0.1), min(10.0, max(maturity * 1.8, maturity + 0.1)), 30)

    spot_grid, volatility_grid = np.meshgrid(heat_spots, heat_volatilities)
    _, maturity_grid = np.meshgrid(heat_spots, heat_maturities)
    price_surface = pricer(S=spot_grid, K=strike, T=maturity, t=0.0, volatility=volatility_grid, r=rate)
    delta_surface = delta(option=option_type, S=spot_grid[: len(heat_maturities)], K=strike, T=maturity_grid, t=0.0, volatility=volatility, r=rate)
    gamma_surface = gamma(S=spot_grid[: len(heat_maturities)], K=strike, T=maturity_grid, t=0.0, volatility=volatility, r=rate)
    vega_surface = vega(S=spot_grid, K=strike, T=maturity, t=0.0, volatility=volatility_grid, r=rate) / 100

    heatmaps = [
        (heat_volatilities, price_surface, "Price by spot and volatility", "Annualized volatility (decimal)", "Option value<br>(ISK)", "volatility", "{:.2f}"),
        (heat_maturities, delta_surface, "Delta by spot and maturity", "Maturity (years)", "Delta<br>(unitless)", "maturity", "{:.4f}"),
        (heat_maturities, gamma_surface, "Gamma by spot and maturity", "Maturity (years)", "Gamma<br>(per ISK)", "maturity", "{:.6g}"),
        (heat_volatilities, vega_surface, "Vega by spot and volatility", "Annualized volatility (decimal)", "Vega<br>(ISK / vol. pp)", "volatility", "{:.4f}"),
    ]
    for y_values, surface, title, y_title, value_title, row_type, value_format in heatmaps:
        show_plot(heatmap_figure(heat_spots, y_values, surface, title, "Spot (ISK)", y_title, value_title))
        with st.expander(f"{title} table"):
            row_labels = (
                [f"{value:.1%}" for value in y_values]
                if row_type == "volatility"
                else [f"{value:.3f}" for value in y_values]
            )
            table = pd.DataFrame(
                [[value_format.format(value) for value in row] for row in surface],
                index=row_labels,
                columns=[f"{value:.2f}" for value in heat_spots],
            )
            table.index.name = "Volatility" if row_type == "volatility" else "Maturity (years)"
            table.columns.name = "Spot (ISK)"
            st.dataframe(table, width="stretch")
