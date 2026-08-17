from .option_info import OptionInfo
from .interest_rate_data import RiskFreeRate

from datetime import date, timedelta
import numpy as np
import pandas as pd

#! this uses fixed pricing_volatility but we should make it rolling

class HedgeEngine():
    def __init__(self, option_type: str, strike_price: float, pricing_volatility: float, start_date: date, end_date: date, current_date: date, stock_price_path: dict | None, option_quantity: float = 1):
        self.stock_price_path = stock_price_path
        self.option_type = option_type
        self.strike_price = strike_price
        self.pricing_volatility = pricing_volatility
        self.start_date = start_date
        self.end_date = end_date
        self.current_date = current_date
        self.option_quantity = option_quantity
        self.option_info = OptionInfo()
        self.risk_free_rate = RiskFreeRate(start_date=self.start_date, end_date=self.end_date)

        
    def get_option_price(self):
        return self.option_info.price(
            option_type=self.option_type, 
            stock_price=self.current_stock_price(),
            strike_price=self.strike_price,
            volatility=self.pricing_volatility,
            rate=self.risk_free_rate,
            start_date=self.start_date, 
            end_date=self.end_date,
            current_date=self.current_date)

    def get_delta(self):
        return self.option_info.option_delta(
            option_type=self.option_type,
            stock_price=self.current_stock_price(), 
            strike_price=self.strike_price, 
            volatility=self.pricing_volatility, 
            rate=self.risk_free_rate,
            start_date=self.start_date, 
            end_date=self.end_date,
            current_date=self.current_date)
        
    def current_stock_price(self):
        #! fix here there if we cant find the date, like in the stock data class
        try:
            return self.stock_price_path[self.current_date]
        except KeyError:
            raise ValueError(f"No price found for {self.current_date}")

    def hedge_amount(self, shares_held: float, current_delta=None):
        """Returns the amount of underlying stock to buy or short. 
        Positive numbers represent the amount of stock to buy, negative number represents amount of stock to short"""
        if current_delta is None:
            current_delta = self.get_delta()
        return (-current_delta * self.option_quantity) - shares_held

    def move_current_date(self, day_offset: int):
        self.current_date = self.current_date + timedelta(days=day_offset)

    def hedge_simulation(self, hedge_interval_days: int):
        if hedge_interval_days <= 0:
            raise ValueError("hedging interval days must be positive")

        hedging_rounds = int(np.ceil((self.end_date - self.current_date).days / hedge_interval_days))
        original_portfolio_value = self.get_option_price() * self.option_quantity
        path_data = list()
        shares_held = 0
        cash_account = 0
        cumulative_transaction_costs = 0.0  # todo update when transaction-cost accounting is implemented

        for _ in range(hedging_rounds):
            current_stock_price = self.current_stock_price()
            current_option_value = self.get_option_price()
            current_delta = self.get_delta()
            shares_to_trade = self.hedge_amount(shares_held=shares_held, current_delta=current_delta)
            shares_held += shares_to_trade

            cash_account -= shares_to_trade * current_stock_price
            
            current_portfolio_value = current_option_value * self.option_quantity + shares_held * current_stock_price + cash_account
            path_data.append({
                "time": self.current_date,
                "stock_price": current_stock_price,
                "option_value": current_option_value,
                "delta": current_delta,
                "shares_held": shares_held,
                "cash_account": cash_account,
                "portfolio_value": current_portfolio_value,
                "cumulative_transaction_costs": cumulative_transaction_costs,
                "profit_loss": current_portfolio_value - original_portfolio_value,
            })

            days_to_move = min(hedge_interval_days, (self.end_date - self.current_date).days)
            cash_account *= np.exp(self.risk_free_rate * days_to_move / 365)
            self.move_current_date(days_to_move)

        current_stock_price = self.current_stock_price()
        if self.option_type == "call":
            option_payoff = max(current_stock_price - self.strike_price, 0)
        elif self.option_type == "put":
            option_payoff = max(self.strike_price - current_stock_price, 0)

        current_portfolio_value = option_payoff * self.option_quantity + shares_held * current_stock_price + cash_account
        final_hedging_error = current_portfolio_value - original_portfolio_value
        path_data.append({
            "time": self.current_date,
            "stock_price": current_stock_price,
            "option_value": option_payoff,
            "delta": 0.0,
            "shares_held": shares_held,
            "cash_account": cash_account,
            "portfolio_value": current_portfolio_value,
            "cumulative_transaction_costs": cumulative_transaction_costs,
            "profit_loss": final_hedging_error,
        })

        path_df = pd.DataFrame(path_data)
        summary = {"final_hedging_error": final_hedging_error, "stock_price": current_stock_price, "option_payoff": option_payoff, "cumulative_transaction_costs": cumulative_transaction_costs}
        return path_df, summary
