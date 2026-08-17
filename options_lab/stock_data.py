import numpy as np
from datetime import date, timedelta
import yfinance as yf
import pandas as pd

from .config import ICELANDIC_MARKET_CLOSED_DATES

class StockData():
    def __init__(self, stock_name):
        self.stock_name = stock_name
        self.stock_ticker = yf.Ticker(stock_name)

        self.raw_stock_data = pd.DataFrame()
        self.adj_stock_data = pd.DataFrame()
        self.populate_stock_data()


    def populate_stock_data(self) -> None:
        if self.raw_stock_data.empty:
            self.raw_stock_data = self.stock_ticker.history(period="max", auto_adjust=False)

        if self.adj_stock_data.empty:
            self.adj_stock_data = self.stock_ticker.history(period="max", auto_adjust=True)


    def adjust_date(self, date: date):
        """Adjust weekend dates to the last trading day"""
        if date in ICELANDIC_MARKET_CLOSED_DATES or date.isoweekday() == 6: # 6 is a saturday
            return self.adjust_date(date - timedelta(days=1))
        if date.isoweekday() == 7: # 7 is sunday
            return self.adjust_date(date - timedelta(days=2))
        return date


    def get_stock_info(self, start_date: date, end_date: date, price_column: str = "Close"):
        if start_date < (first_date := self.adj_stock_data.index.min().date()):
            start_date = first_date

        if end_date > (last_date := self.adj_stock_data.index.max().date()):
            end_date = last_date

        stock_info = self.adj_stock_data[(self.adj_stock_data.index.date >= self.adjust_date(start_date)) & (self.adj_stock_data.index.date <= self.adjust_date(end_date))]
        return stock_info[[price_column, "Volume"]].rename_axis("Date").reset_index()


    def get_current_stock_price(self, current_date: date, price_column: str = "Close") -> float:
        prices = self.adj_stock_data.loc[self.adj_stock_data.index.date <= self.adjust_date(current_date), price_column]
        return float(prices.iloc[-1])

    
    def get_volatility(self, lookback_days: int = 60, current_date: date = date.today(), price_column: str = "Close") -> float:
        start_date = self.adjust_date(current_date - timedelta(days=max(30, lookback_days)))

        prices = self.raw_stock_data.loc[
            (self.raw_stock_data.index.date >= start_date)
            & (self.raw_stock_data.index.date <= current_date),
            price_column
        ].to_numpy()

        log_returns = np.diff(np.log(prices))
        return np.std(log_returns, ddof=1) * np.sqrt(252)
