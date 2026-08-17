from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ui.components import empty_state


ACCENT = "#4993F3"
COLORS = (ACCENT, "#3DBEF5", "#FBCB50", "#A78BFA", "#FB7185")
LINE_COLORS = (ACCENT, "#FBCB50", "#3DBEF5", "#A78BFA", "#FB7185")
PLOT_CONFIG = {"displaylogo": False, "responsive": True}


def line_figure(
    data: pd.DataFrame,
    x: str,
    series: list[str],
    title: str,
    x_title: str,
    y_title: str,
) -> go.Figure:
    figure = go.Figure()
    for index, column in enumerate(series):
        figure.add_trace(
            go.Scatter(
                x=data[x],
                y=data[column],
                mode="lines",
                name=column,
                line={"color": LINE_COLORS[index % len(LINE_COLORS)], "width": 2},
                hovertemplate=f"{x}: %{{x:,.4f}}<br>{column}: %{{y:,.6f}}<extra></extra>",
            )
        )
    return style_figure(figure, title, x_title, y_title)


def heatmap_figure(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    title: str,
    x_title: str,
    y_title: str,
    value_title: str,
) -> go.Figure:
    figure = go.Figure(
        go.Heatmap(
            x=x,
            y=y,
            z=z,
            colorscale="Cividis",
            colorbar={
                "title": {"text": value_title, "side": "top", "font": {"size": 13}},
                "tickfont": {"size": 13},
                "ticks": "outside",
                "ticklen": 5,
                "thickness": 36,
                "len": 0.92,
                "x": 0.87,
                "xanchor": "left",
                "outlinewidth": 0,
            },
            hovertemplate=(
                f"{x_title}: %{{x:,.4f}}<br>{y_title}: %{{y:,.4f}}"
                f"<br>{value_title}: %{{z:,.6f}}<extra></extra>"
            ),
        )
    )
    figure = style_figure(figure, title, x_title, y_title)
    figure.update_xaxes(domain=[0.0, 0.82])
    return figure


def style_figure(figure: go.Figure, title: str, x_title: str, y_title: str) -> go.Figure:
    figure.update_layout(
        title={"text": title, "x": 0.01, "xanchor": "left", "font": {"family": "Geist, sans-serif"}},
        xaxis_title=x_title,
        yaxis_title=y_title,
        template="plotly_dark",
        paper_bgcolor="#101823",
        plot_bgcolor="#101823",
        font={"color": "#CED5DE", "family": "Inter, sans-serif"},
        hoverlabel={"font_family": "Inter, sans-serif"},
        legend={"orientation": "h", "y": 1.08, "x": 0},
        margin={"l": 48, "r": 24, "t": 72, "b": 48},
        height=390,
    )
    figure.update_xaxes(gridcolor="#2B3B50", zerolinecolor="#61728A")
    figure.update_yaxes(gridcolor="#2B3B50", zerolinecolor="#61728A")
    return figure


def show_plot(figure: go.Figure) -> None:
    st.plotly_chart(figure, width="stretch", config=PLOT_CONFIG)



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
    ``profit_loss`` is optional. ``summary`` may contain ``final_hedging_error``.
    No values are calculated here.
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

    chart_specs = [
        (["stock_price"], "Stock price through time", "Price (ISK)"),
        (["option_value"], "Option value through time", "Value (ISK)"),
        (["shares_held"], "Shares held", "Shares"),
        (["cash_account", "portfolio_value"], "Cash and portfolio value", "Value (ISK)"),
        (["cumulative_transaction_costs"], "Cumulative transaction costs", "Costs (ISK)"),
    ]
    if "profit_loss" in data.columns:
        chart_specs.append((["profit_loss"], "Hedged portfolio profit / loss", "Profit / loss (ISK)"))

    for index in range(0, len(chart_specs), 2):
        row = chart_specs[index : index + 2]
        for container, (series, title, unit) in zip(st.columns(len(row)), row):
            with container:
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
