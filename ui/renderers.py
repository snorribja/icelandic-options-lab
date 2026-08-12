from __future__ import annotations

from collections.abc import Mapping

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ui.dashboard import ACCENT, COLORS, empty_state, line_figure, show_plot, style_figure


def _frame(value: pd.DataFrame | Mapping | None) -> pd.DataFrame | None:
    if value is None:
        return None
    if isinstance(value, pd.DataFrame):
        return value
    try:
        return pd.DataFrame(value)
    except ValueError:
        return pd.DataFrame([value])


def render_hedging_results(
    path: pd.DataFrame | Mapping | None,
    summary: Mapping | None = None,
) -> None:
    """Render a hedge path with columns time, stock_price, option_value, delta,
    shares_held, cash_account, portfolio_value, and cumulative_transaction_costs.
    ``summary`` may contain ``final_hedging_error``. No values are calculated here.
    """
    data = _frame(path)
    if data is None or data.empty:
        empty_state(
            "Awaiting path data",
            "Delta-hedging engine not connected yet. Configure the scenario now; results will appear here once the engine supplies a path DataFrame.",
        )
        return

    required = {
        "time",
        "stock_price",
        "option_value",
        "delta",
        "shares_held",
        "cash_account",
        "portfolio_value",
        "cumulative_transaction_costs",
    }
    missing = sorted(required.difference(data.columns))
    if missing:
        st.error(f"Hedge path is missing required columns: {', '.join(missing)}.")
        return

    if summary and "final_hedging_error" in summary:
        st.metric("Final hedging error", f"{summary['final_hedging_error']:,.4f} ISK")

    chart_specs = (
        (["stock_price"], "Stock price through time", "Price (ISK)"),
        (["option_value"], "Option value through time", "Value (ISK)"),
        (["delta", "shares_held"], "Delta and shares held", "Units"),
        (["cash_account", "portfolio_value"], "Cash and portfolio value", "Value (ISK)"),
        (["cumulative_transaction_costs"], "Cumulative transaction costs", "Costs (ISK)"),
    )
    for left, right in zip(chart_specs[::2], chart_specs[1::2]):
        columns = st.columns(2)
        for container, (series, title, unit) in zip(columns, (left, right)):
            with container:
                show_plot(line_figure(data, "time", series, title, "Time", unit))
    series, title, unit = chart_specs[-1]
    show_plot(line_figure(data, "time", series, title, "Time", unit))

    with st.expander("Path data table"):
        st.dataframe(data, width="stretch", hide_index=True)


def render_monte_carlo_results(
    results: pd.DataFrame | Mapping | None,
    summary_statistics: pd.DataFrame | Mapping | None,
) -> None:
    """Render future Monte Carlo output.

    ``results`` expects error, hedge_frequency, realized_volatility, and
    transaction_costs columns. ``summary_statistics`` is a precomputed DataFrame
    or dictionary containing mean, median, standard_deviation, rmse, p05, p95,
    minimum, and maximum. This function never computes research statistics.
    """
    st.subheader("Summary statistics")
    summary = _frame(summary_statistics)
    if summary is None or summary.empty:
        st.info("No precomputed summary statistics supplied.")
    else:
        st.dataframe(summary, width="stretch", hide_index=True)

    data = _frame(results)
    if data is None or data.empty:
        empty_state(
            "Awaiting Monte Carlo results",
            "Monte Carlo engine not connected yet. Results, distribution charts, and CSV export will appear after it supplies a results DataFrame and precomputed statistics.",
        )
        return

    required = {"error", "hedge_frequency", "realized_volatility", "transaction_costs"}
    missing = sorted(required.difference(data.columns))
    if missing:
        st.error(f"Monte Carlo results are missing required columns: {', '.join(missing)}.")
        return

    first, second = st.columns(2)
    with first:
        histogram = px.histogram(data, x="error", title="Hedging-error distribution", color_discrete_sequence=[ACCENT])
        show_plot(style_figure(histogram, "Hedging-error distribution", "Hedging error (ISK)", "Simulation count"))
    with second:
        boxplot = px.box(
            data,
            x="hedge_frequency",
            y="error",
            title="Error by hedge frequency",
            color_discrete_sequence=[COLORS[1]],
        )
        show_plot(style_figure(boxplot, "Frequency comparison", "Hedge frequency", "Hedging error (ISK)"))

    first, second = st.columns(2)
    with first:
        volatility = px.scatter(
            data,
            x="realized_volatility",
            y="error",
            title="Error vs realized volatility",
            color_discrete_sequence=[COLORS[2]],
        )
        show_plot(style_figure(volatility, "Error vs realized volatility", "Realized volatility (annualized decimal)", "Hedging error (ISK)"))
    with second:
        frequency = px.scatter(
            data,
            x="hedge_frequency",
            y="error",
            title="Error vs hedge frequency",
            color_discrete_sequence=[COLORS[3]],
        )
        show_plot(style_figure(frequency, "Error vs hedge frequency", "Hedge frequency", "Hedging error (ISK)"))

    costs = go.Figure(
        go.Box(
            x=data["hedge_frequency"],
            y=data["transaction_costs"],
            name="Transaction costs",
            marker_color=COLORS[4],
            boxmean=False,
        )
    )
    show_plot(style_figure(costs, "Transaction costs vs hedge frequency", "Hedge frequency", "Transaction costs (ISK)"))
    st.download_button(
        "Download results as CSV",
        data.to_csv(index=False).encode("utf-8"),
        file_name="monte_carlo_results.csv",
        mime="text/csv",
    )


def render_research_experiment(
    results: pd.DataFrame | Mapping | None,
    summary_statistics: pd.DataFrame | Mapping | None,
    interpretation: str | None,
    *,
    x: str,
    y: str,
    chart_title: str,
) -> None:
    """Render supplied experiment data, precomputed statistics, and interpretation.

    ``results`` must contain the named x/y columns. The caller—not this renderer—
    owns calculations and interpretation text.
    """
    st.markdown("##### Summary statistics")
    summary = _frame(summary_statistics)
    if summary is None or summary.empty:
        st.caption("No precomputed statistics supplied.")
    else:
        st.dataframe(summary, width="stretch", hide_index=True)

    st.markdown("##### Chart")
    data = _frame(results)
    if data is None or data.empty:
        st.info("Experiment runner not connected. No research results are displayed.")
    elif missing := sorted({x, y}.difference(data.columns)):
        st.error(f"Experiment results are missing required columns: {', '.join(missing)}.")
    else:
        show_plot(line_figure(data, x, [y], chart_title, x.replace("_", " ").title(), y.replace("_", " ").title()))
        with st.expander("Experiment data table"):
            st.dataframe(data, width="stretch", hide_index=True)

    st.markdown("##### Interpretation")
    if interpretation:
        st.write(interpretation)
    else:
        st.caption("No interpretation supplied. Conclusions are never generated by the dashboard.")
