import pandas as pd
import streamlit as st

from ui.components import configure_page, page_intro


configure_page("Model & Data")
page_intro(
    "Model & Data",
    "What the repository implements today, the units presented by this dashboard, and the research functionality that remains separate.",
)

implemented_tab, limitations_tab, planned_tab = st.tabs(["Currently implemented", "Assumptions & limitations", "Planned research"])

with implemented_tab:
    st.subheader("Black–Scholes implementation")
    st.markdown(
        "- European call and put pricing in `options_lab/pricing.py`\n"
        "- No dividend yield\n"
        "- Decimal rate and volatility inputs\n"
        "- `T` and `t` measured in years, with time to maturity equal to `T - t`\n"
        "- `OptionInfo` converts dates using calendar days divided by 365 and selects the existing call or put function"
    )

    st.subheader("Greeks and dashboard units")
    st.dataframe(
        pd.DataFrame(
            [
                ("Delta", "Change in option value per unit spot change", "Raw model value"),
                ("Gamma", "Change in Delta per unit spot change", "Raw model value"),
                ("Vega", "Sensitivity to an absolute volatility change", "Model value / 100 per percentage point"),
                ("Theta", "Sensitivity to elapsed time in years", "Model value / 365 per calendar day"),
                ("Rho", "Sensitivity to an absolute rate change", "Model value / 100 per percentage point"),
            ],
            columns=["Greek", "Existing implementation", "Dashboard display"],
        ),
        width="stretch",
        hide_index=True,
    )

    st.subheader("Stock data")
    st.markdown(
        "`StockData` retrieves maximum-period raw and adjusted history through Yahoo Finance (`yfinance`). "
        "Current price uses adjusted Close. Historical volatility uses raw Close log returns, sample standard deviation "
        "(`ddof=1`), and annualization by the square root of 252 trading days."
    )

    st.subheader("Icelandic interest rates")
    st.markdown(
        "`RiskFreeRate` returns a continuously compounded annual ISK rate. Up to six months it selects the nearest "
        "configured REIBOR maturity from Central Bank of Iceland data. For longer terms it uses Central Bank fixed-term "
        "series where available and falls back to the configured Nasdaq fixed-duration yield workbook when those series "
        "are unavailable. The supported interval is greater than zero and no more than ten years."
    )

    st.subheader("Dates and market closures")
    st.markdown(
        "`StockData.adjust_date` moves weekends and dates listed in `ICELANDIC_MARKET_CLOSED_DATES` backward to the latest "
        "eligible date. The committed closure list covers 2009 through 3 August 2026; it is static rather than a live exchange calendar."
    )

with limitations_tab:
    st.subheader("Model limitations")
    st.markdown(
        "- Constant volatility and interest rate over the option life\n"
        "- Lognormal returns and continuous trading\n"
        "- No jumps or dividend yield\n"
        "- Historical rather than implied volatility\n"
        "- European exercise only"
    )
    st.subheader("Market and data limitations")
    st.markdown(
        "- Icelandic equity liquidity and price-discovery constraints\n"
        "- Scarcity of listed Icelandic equity options\n"
        "- Yahoo Finance, Central Bank, and Nasdaq availability and revision risk\n"
        "- Static market-closure coverage after the latest configured date\n"
        "- General model, estimation, and data-source risk"
    )

with planned_tab:
    st.subheader("Not implemented in the current repository")
    st.warning("The items below are UI destinations, not claims of available research output.")
    st.markdown(
        "- GBM/path simulation\n"
        "- Discrete delta-hedging, cash-account, and transaction-cost accounting\n"
        "- Monte Carlo simulation and hedging-error statistics\n"
        "- Research experiment runners and automatic interpretations\n"
        "- Alternative pricing models"
    )
