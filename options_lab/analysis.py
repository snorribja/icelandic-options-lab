import numpy as np
import pandas as pd

from .pricing import (
    call_option_price,
    delta,
    gamma,
    put_option_price,
    rho,
    theta,
    vega,
)


def price_function(option_type: str):
    if option_type == "call":
        return call_option_price
    if option_type == "put":
        return put_option_price
    raise ValueError("option_type must be 'call' or 'put'")


def price_and_greeks(
    option_type: str,
    spot: float | np.ndarray,
    strike: float,
    maturity: float | np.ndarray,
    volatility: float | np.ndarray,
    rate: float,
) -> dict[str, float | np.ndarray]:
    """Call the existing model functions without adding pricing logic."""
    arguments = {
        "S": spot,
        "K": strike,
        "T": maturity,
        "t": 0.0,
        "volatility": volatility,
        "r": rate,
    }
    return {
        "Price": price_function(option_type)(**arguments),
        "Delta": delta(option=option_type, **arguments),
        "Gamma": gamma(**arguments),
        "Vega": vega(**arguments),
        "Theta": theta(option=option_type, **arguments),
        "Rho": rho(option=option_type, **arguments),
    }


def spot_sensitivity_frame(
    option_type: str,
    spot: float,
    strike: float,
    volatility: float,
    maturity: float,
    rate: float,
    points: int = 81,
    width: float = 0.5,
) -> pd.DataFrame:
    spots = np.linspace(max(0.01, spot * (1 - width)), spot * (1 + width), points)
    values = price_and_greeks(option_type, spots, strike, maturity, volatility, rate)
    values["Vega"] = values["Vega"] / 100
    values["Theta"] = values["Theta"] / 365
    values["Rho"] = values["Rho"] / 100
    return pd.DataFrame({"Spot": spots, **values})


