from .hedging import HedgeEngine
import pandas as pd
import numpy as np

import numpy as np
import pandas as pd


class MonteCarlo:
    def __init__(self, sims, hedge_freq, option_type, strike_price, start_date, end_date, option_quantity):
        self.sims = sims
        self.hedge_freq = hedge_freq
        self.option_type = option_type
        self.strike_price = strike_price
        self.start_date = start_date
        self.end_date = end_date
        self.option_quantity = option_quantity

    def generate_stock_prices(self):
        #use gbm
        raise NotImplementedError

    def run(self):
        hedging_summaries = list()

        hedge_engine = HedgeEngine(
            option_type=self.option_type,
            strike_price=self.strike_price,
            start_date=self.start_date,
            end_date=self.end_date,
            current_date=self.start_date,
            option_quantity=self.option_quantity,
            pricing_volatility=
        )

        for sim_num in self.sims:
            hedge_engine.stock_price_path = self.generate_stock_prices()
            for hid in self.hedge_freq:
                _, hedging_summary = hedge_engine.hedge_simulation(hedge_interval_days=hid)
                hedging_summary.update({"hedge_interval_days": hid,"sim_id": sim_num})
                hedging_summaries.append(hedging_summary)

        results_df = pd.DataFrame(hedging_summaries)
        summary_df = (
            results_df
            .groupby("hedge_interval_days", as_index=False)
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
            )
        )

        return results_df, summary_df