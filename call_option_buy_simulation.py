import random
from global_vars import ICELANDIC_STOCKS
from data_retriever import call_option_stock_price, get_current_stock_price

from datetime import timedelta, date
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf


def get_random_stock():
    stock_names = list(ICELANDIC_STOCKS.keys())
    n = len(stock_names)
    stock_number = random.randint(0, n-1)
    return stock_names[stock_number]
    

def get_random_dates(stock_name):
    stock_ticker = yf.Ticker(stock_name)
    hist = stock_ticker.history(period="max")
    first_date = hist.index.min().date()
    last_date = hist.index.max().date()
    days_diff = (last_date - first_date).days

    while True:
        end = random.randint(0, days_diff - 30)
        start = random.randint(end, days_diff)
        diff = start - end
        start_date, end_date = date.today() - timedelta(days=start), date.today() - timedelta(days=end)
        if diff > 30 and diff < 10*365 and start_date in hist.index and end_date in hist.index:
            break
    return start_date, end_date


def simulate_call():
    number_of_sims = 10
    gain_loss = list()
    buy_budget = 100
    for _ in range(number_of_sims):
        try:
            stock_name = get_random_stock()
            start_date, end_date = get_random_dates(stock_name=stock_name)

            start_stock_price, end_stock_price = get_current_stock_price(stock_name=stock_name, current_date=start_date), get_current_stock_price(stock_name=stock_name, current_date=end_date)

            strike_price = start_stock_price * 1.05
            call_option_price = call_option_stock_price(stock_name=stock_name, strike_price=strike_price, start_date=start_date, end_date=end_date, current_date=start_date)
            buy_ratio = buy_budget / call_option_price

            if not np.isfinite(call_option_price) or call_option_price <= 0:
                print(f"Invalid option price: {call_option_price}")
                continue

            gain_loss.append((max(end_stock_price - strike_price, 0) - call_option_price) * buy_ratio) 
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
plt.xlabel("Time")
plt.ylabel("Cumulative gain/loss")
plt.title("Cumulative Gain/Loss")
plt.grid(True)
plt.show()
    