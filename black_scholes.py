import numpy as np
import scipy

"""
T is the time of option expiration. (measured in years)
tau (τ) is the time until maturity: τ=T-t
K is the strike price of the option, also known as the exercise price.
r = annual risk-free interest rate
"""

# without dividends
def call_option_price(S: float, K: float, T: float, t: float, volatility: float, r: float) -> float:
    tau = T - t 
    D = discount_factor(r=r, tau=tau)
    F = forward_price(S=S, D=D)
    d_plus = d(sign="+", K=K, tau=tau, volatility=volatility, F=F)
    d_minus = d(sign="-", K=K, tau=tau, volatility=volatility, F=F)
    forward_component = scipy.stats.norm.cdf(d_plus) * F
    strike_component = scipy.stats.norm.cdf(d_minus) * K
    return D * (forward_component - strike_component)

# without dividends
def put_option_price(S: float, K: float, T: float, t: float, volatility: float, r: float) -> float:
    tau = T - t 
    D = discount_factor(r=r, tau=tau)
    F = forward_price(S=S, D=D)
    d_plus = d(sign="+", K=K, tau=tau, volatility=volatility, F=F)
    d_minus = d(sign="-", K=K, tau=tau, volatility=volatility, F=F)
    forward_component = scipy.stats.norm.cdf(-d_plus) * F
    strike_component = scipy.stats.norm.cdf(-d_minus) * K
    return D * (strike_component - forward_component)

def d(sign: str, K: float, tau: float, volatility: float, F: float) -> float:
    d_plus = (1 / (volatility * np.sqrt(tau))) * ((np.log(F / K)) + (0.5 * (volatility ** 2) * tau))
    if sign == "+":
        return d_plus
    elif sign == "-":
        return d_plus - (volatility * np.sqrt(tau))

def discount_factor(r: float, tau: float) -> float:
    return np.exp(-r * tau)

def forward_price(S: float, D: float) -> float:
    return S / D


# The Greek 

def delta(option: str, S: float, K: float, T: float, t: float, volatility: float, r: float) -> float:
    tau = T - t 
    D = discount_factor(r=r, tau=tau)
    F = forward_price(S=S, D=D)
    d_plus = d(sign="+", volatility=volatility, tau=tau, F=F, K=K)
    call_delta = scipy.stats.norm.cdf(d_plus)
    if option == "call":
        return call_delta
    elif option == "put":
        return scipy.stats.norm.cdf(d_plus) - 1

def gamma(S: float, K: float, T: float, t: float, volatility: float, r: float) -> float:
    tau = T - t
    D = discount_factor(r=r, tau=tau)
    F = forward_price(S=S, D=D)
    d_plus = d(sign="+", volatility=volatility, tau=tau, F=F, K=K)

    return (scipy.stats.norm.pdf(d_plus) / (S * volatility * np.sqrt(tau)))


