import random
from datetime import date, timedelta

import matplotlib.pyplot as plt
import numpy as np

from interest_rate_data import RiskFreeRate
from option_pricing import OptionPricing
from stock_data import StockData

random.seed(202)

STOCK_NAME = "FESTI.IC"

def get_random_date(stock_data):
    dates = stock_data.adj_stock_data.index.date
    return random.choice([day for day in dates if 360 < (date.today() - day).days < 10 * 365])


def plot_stock(stock_history, start_date, strike_price, call_option_price, profit_loss):
    plt.figure(figsize=(12, 6), facecolor="#111111")
    ax = plt.gca()
    ax.set_facecolor("#111111")
    plt.plot(stock_history["Date"], stock_history["Close"], linewidth=2)

    plt.axhline(y=strike_price, linestyle="--", linewidth=1.5, label=f"Strike: {strike_price:.2f}")
    plt.axvline(x=start_date, linestyle="--", linewidth=1)

    plt.title(f"{STOCK_NAME} | Option: {call_option_price:.2f} | P/L: {profit_loss:.2f}%", color="white", fontsize=14)
    plt.xlabel("Date", color="white")
    plt.ylabel("Price", color="white")

    ax.yaxis.set_major_locator(plt.MaxNLocator(6))
    ax.xaxis.set_major_locator(plt.MaxNLocator(7))

    ax.tick_params(colors="white")

    for spine in ax.spines.values():
        spine.set_color("#444444")

    plt.grid(True, linestyle="--", alpha=0.15)

    plt.legend(facecolor="#111111", labelcolor="white")

    plt.tight_layout()
    plt.show()


def simulate_call():
    stock_data = StockData(STOCK_NAME)
    start_date = get_random_date(stock_data)
    end_date = stock_data.adjust_date(start_date + timedelta(days=360))
    print(f"{STOCK_NAME} - {start_date} -> {end_date}")

    stock_history = stock_data.get_stock_info(start_date - timedelta(5), end_date + timedelta(5))
    start_stock_price = stock_data.get_current_stock_price(start_date)
    end_stock_price = stock_data.get_current_stock_price(end_date)

    strike_price = start_stock_price * 1.05
    call_option_price = OptionPricing().price(
        option_type="call",
        stock_price=start_stock_price,
        strike_price=strike_price,
        volatility=stock_data.get_volatility(current_date=start_date),
        rate=RiskFreeRate(start_date, end_date),
        start_date=start_date,
        end_date=end_date,
        current_date=start_date,
    )

    if not np.isfinite(call_option_price) or call_option_price <= 0:
        raise ValueError(f"Invalid option price: {call_option_price}")

    profit_loss = ((max(end_stock_price - strike_price, 0) - call_option_price) / call_option_price) * 100

    plot_stock(stock_history, start_date, strike_price, call_option_price, profit_loss)

    
if __name__ == "__main__":
    simulate_call()
