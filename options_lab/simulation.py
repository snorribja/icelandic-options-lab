from .hedging import HedgeEngine
from .stock_data import StockData
from datetime import timedelta
import pandas as pd
import numpy as np
import streamlit as st

#! add random seed functionality

@st.cache_data(ttl=3600, show_spinner=False)
def load_adjusted_stock_data(stock_name):
    return StockData(stock_name=stock_name).adj_stock_data

# Currently normal monte carlo not student t monte carlo
class MonteCarlo:
    def __init__(self, stock_name, sims, hedge_freq, option_type, strike_price, start_date, end_date, transaction_cost_per, option_quantity):
        self.sims = sims
        self.hedge_freq = hedge_freq
        self.option_type = option_type
        self.strike_price = strike_price
        self.start_date = start_date
        self.end_date = end_date
        self.transaction_cost_per = transaction_cost_per
        self.option_quantity = option_quantity
        self.adj_stock_data = load_adjusted_stock_data(stock_name).copy()
        self.n_days = (end_date - start_date).days
        self.historical_annual_vol = 0
        self.stock_price_matrix = self.generate_stock_prices_matrix()

    def generate_stock_prices_matrix(self):
        close_prices = self.adj_stock_data["Close"]
        log_returns = np.log(close_prices / close_prices.shift(1)).dropna().to_numpy()
        ave_drift = log_returns.mean() # average drift
        historical_daily_vol = log_returns.std(ddof=1)
        self.historical_annual_vol = historical_daily_vol * np.sqrt(252)

        shocks = np.random.normal(0, 1, size=(self.n_days, self.sims))

        # GBM simulated log returns
        simulated_log_returns = (ave_drift + historical_daily_vol * shocks)

        current_stock_price = self.adj_stock_data["Close"].dropna().iloc[-1]

        simulated_prices = current_stock_price * np.exp(np.cumsum(simulated_log_returns, axis=0))
        return np.vstack([np.full((1, self.sims), current_stock_price), simulated_prices]) # including the stocks starting price

    def run(self):
        hedging_summaries = list()

        hedge_engine = HedgeEngine(
            option_type=self.option_type,
            strike_price=self.strike_price,
            start_date=self.start_date,
            end_date=self.end_date,
            current_date=self.start_date,
            option_quantity=self.option_quantity,
            transaction_cost_per=self.transaction_cost_per,
            pricing_volatility=self.historical_annual_vol,
        )

        for sim_num in range(self.sims):
            hedge_engine.stock_price_path = {self.start_date + timedelta(days=i): float(day[sim_num]) for i, day in enumerate(self.stock_price_matrix)}

            stock_price_path = dict()
            deltadays = 0
            date = self.start_date + timedelta(days=deltadays)
            for day in self.stock_price_matrix:
                price = float(day[sim_num])
                stock_price_path[date] = price
                deltadays += 1
                date = self.start_date + timedelta(days=deltadays)
                while date.isoweekday() == 6 or date.isoweekday() == 7:
                    stock_price_path[date] = price
                    deltadays += 1
                    date = self.start_date + timedelta(days=deltadays)
            hedge_engine.stock_price_path = stock_price_path

            for hid in self.hedge_freq:
                hedge_engine.current_date = self.start_date
                _, hedging_summary = hedge_engine.hedge_simulation(hid)
                hedging_summary.update(
                    {
                        "error": hedging_summary["final_hedging_error"],
                        "hedge_frequency": hid,
                        #"realized_volatility": self.historical_annual_vol,
                        "transaction_costs": hedging_summary["cumulative_transaction_costs"],
                        "net_result": hedging_summary["net_result"],
                        "net_result_percentage": hedging_summary["net_result_percentage"],
                        "sim_id": sim_num,
                    }
                )
                hedging_summaries.append(hedging_summary)

        results_df = pd.DataFrame(hedging_summaries)
        summary_df = (
            results_df
            .groupby("hedge_frequency", as_index=False)
            .agg(
                simulations=("final_hedging_error", "size"),
                mean=("final_hedging_error", "mean"),
                median=("final_hedging_error", "median"),
                standard_deviation=("final_hedging_error", "std"),
                rmse=("final_hedging_error", lambda values: np.sqrt(np.mean(values**2))),
                p05=("final_hedging_error", lambda values: values.quantile(0.05)),
                p95=("final_hedging_error", lambda values: values.quantile(0.95)),
                minimum=("final_hedging_error", "min"),
                maximum=("final_hedging_error", "max"),
                mean_transaction_costs=("cumulative_transaction_costs", "mean"),
                mean_net_result=("net_result", "mean"),
                mean_net_result_percentage=("net_result_percentage", "mean"),
            )
        )

        return results_df, summary_df
