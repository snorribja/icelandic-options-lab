import random
from global_vars import ICELANDIC_STOCKS, ICELANDIC_MARKET_CLOSED_DATES
from data_retriever import call_option_stock_price, get_current_stock_price

from datetime import timedelta, date
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf


def adjust_date(date: date):
    """Adjust weekend dates to the last trading day"""
    if date in ICELANDIC_MARKET_CLOSED_DATES or date.isoweekday() == 6: # 6 is a saturday
        return adjust_date(date - timedelta(days=1))
    if date.isoweekday() == 7: # 7 is sunday
        return adjust_date(date - timedelta(days=2))
    return date


def get_random_stock():
    stock_names = list(ICELANDIC_STOCKS.keys())
    n = len(stock_names)
    stock_number = random.randint(0, n-1)
    return stock_names[stock_number]
    

def get_random_dates(stock_name):
    hist = yf.Ticker(stock_name).history(period="max")
    dates = hist.index.date
    while True:
        start_date, end_date = sorted(random.sample(list(dates), 2))
        delta = (end_date - start_date).days
        if 30 < delta < 10 * 365:
            return start_date, end_date


def simulate_call():
    number_of_sims = 20
    gain_loss = list()
    buy_budget = 100
    for _ in range(number_of_sims):
        try:
            stock_name = get_random_stock()
            start_date, end_date = get_random_dates(stock_name=stock_name)
            print(f"{stock_name} - {start_date} -> {end_date}")

            start_stock_price, end_stock_price = get_current_stock_price(stock_name=stock_name, current_date=start_date), get_current_stock_price(stock_name=stock_name, current_date=end_date)

            strike_price = start_stock_price * 1.05
            call_option_price = call_option_stock_price(stock_name=stock_name, strike_price=strike_price, start_date=start_date, end_date=end_date, current_date=start_date)
            buy_ratio = buy_budget / call_option_price

            if not np.isfinite(call_option_price) or call_option_price <= 0:
                print(f"Invalid option price: {call_option_price}")
                continue

            gain_loss.append(max(end_stock_price - strike_price, 0) * buy_ratio - buy_budget) 
        except:
            continue
    return gain_loss
        

gain_loss = simulate_call()

cum_gain_loss = list()

for i in range(len(gain_loss)):
    cum_gain_loss.append(sum(gain_loss[:i+1]))

print(cum_gain_loss)
print()
print(sum(gain_loss))
print(np.average(gain_loss))
print(len(cum_gain_loss))
plt.plot(cum_gain_loss)
plt.xlabel("Stocks")
plt.ylabel("Cumulative gain/loss")
plt.title("Cumulative Gain/Loss")
plt.grid(True)
plt.show()
    