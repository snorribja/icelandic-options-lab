from datetime import date

from black_scholes import call_option_price, put_option_price, delta, gamma


class OptionInfo():
    def price(self, option_type: str, stock_price: float, strike_price: float, volatility: float, rate: float, start_date: date, end_date: date, current_date: date = date.today()):
        pricer = {
            "call": call_option_price,
            "put": put_option_price,
        }.get(option_type)

        if pricer is None:
            raise ValueError("option_type must be 'call' or 'put'")

        T, t = self.get_T_and_t(start_date=start_date, end_date=end_date, current_date=current_date)        

        return pricer(S=stock_price, K=strike_price, T=T, t=t, volatility=volatility, r=rate)

    def get_T_and_t(self, start_date: date, end_date: date, current_date: date = date.today()):
        return (end_date - start_date).days / 365, (current_date - start_date).days / 365

    def option_delta(self, option_type: str, stock_price: float, strike_price: float, volatility: float, rate: float, start_date: date, end_date: date, current_date: date = date.today()):
        T, t = self.get_T_and_t(start_date=start_date, end_date=end_date, current_date=current_date) 
        return delta(option=option_type, S=stock_price, K=strike_price, T=T, t=t, volatility=volatility, r=rate)

    def option_gamma(self, stock_price: float, strike_price: float, volatility: float, rate: float, start_date: date, end_date: date, current_date: date = date.today()):
        T, t = self.get_T_and_t(start_date=start_date, end_date=end_date, current_date=current_date) 
        return gamma(S=stock_price, K=strike_price, T=T, t=t, volatility=volatility, r=rate)
