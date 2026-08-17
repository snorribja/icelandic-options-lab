import matplotlib.pyplot as plt
from datetime import date, timedelta

from options_lab.hedging import HedgeEngine
from options_lab.stock_data import StockData


def unhedged_profit_loss_progress(hedge_engine, hedge_interval_days):
    original_portfolio_value = hedge_engine.original_option_price * hedge_engine.option_quantity
    profit_loss_progress = list()

    while hedge_engine.current_date < hedge_engine.end_date:
        current_option_value = hedge_engine.get_option_price() * hedge_engine.option_quantity
        profit_loss_progress.append(current_option_value - original_portfolio_value)
        days_to_move = min(hedge_interval_days, (hedge_engine.end_date - hedge_engine.current_date).days)
        hedge_engine.move_current_date(days_to_move)

    current_stock_price = hedge_engine.current_stock_price()
    if hedge_engine.option_type == "call":
        option_payoff = max(current_stock_price - hedge_engine.strike_price, 0)
    else:
        option_payoff = max(hedge_engine.strike_price - current_stock_price, 0)

    profit_loss_progress.append(option_payoff * hedge_engine.option_quantity - original_portfolio_value)
    return profit_loss_progress


def plot_profit_loss_progress(profit_loss_progress, unhedged_profit_loss_progress, output_path="reports/figures/hedging_progress.png"):
    plt.figure(figsize=(12, 6), facecolor="#111111")
    ax = plt.gca()
    ax.set_facecolor("#111111")
    plt.plot(profit_loss_progress, color="#4993f3", linewidth=2, label="Hedged portfolio P/L")
    plt.plot(unhedged_profit_loss_progress, color="#fbcb50", linewidth=2, label="Unhedged option P/L")
    plt.axhline(y=0, color="#9ca6b4", linestyle="--", linewidth=1.5, label="Break-even")

    plt.title("Hedged vs unhedged option P/L", color="white", fontsize=14)
    plt.xlabel("Hedge step", color="white")
    plt.ylabel("P/L (ISK)", color="white")

    ax.yaxis.set_major_locator(plt.MaxNLocator(6))
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.tick_params(colors="white")

    for spine in ax.spines.values():
        spine.set_color("#444444")

    plt.grid(True, linestyle="--", alpha=0.15)
    plt.legend(facecolor="#111111", labelcolor="white")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, facecolor="#111111")
    plt.close()
    print(f"Saved plot to {output_path}")


if __name__ == "__main__":
    start_date = date(2024, 1, 1)
    end_date = date(2025, 1, 1)
    current_date = date(2024, 1, 1)
    stock_data = StockData("ALVO.IC")
    stock_price_path = {
        start_date + timedelta(days=day): stock_data.get_current_stock_price(start_date + timedelta(days=day))
        for day in range((end_date - start_date).days + 1)
    }
    pricing_volatility = stock_data.get_volatility(current_date=start_date)
    he = HedgeEngine(stock_price_path, "call", 1700, pricing_volatility, start_date, end_date, current_date, option_quantity=100)
    unhedged_progress = unhedged_profit_loss_progress(he, 7)
    he.current_date = current_date
    path_df, summary = he.hedge_simulation(7)
    profit_loss_progress = path_df["profit_loss"].tolist()
    print(summary)
    plot_profit_loss_progress(profit_loss_progress, unhedged_progress)
        
