from .simulation import MonteCarlo
from datetime import date
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import skew, kurtosis

stock_name = "SKAGI.IC"

sims = 300
hedge_freq = 30
option_type = "call"
strike_price = 105
start_date = date.today() 
end_date = date(2027, 11, 1)
option_quantity = 100

mc = MonteCarlo(stock_name, sims, hedge_freq, option_type, strike_price, start_date, end_date, option_quantity)

price_path = mc.generate_stock_prices_matrix()

plt.figure()
plt.plot(price_path)
plt.show()
