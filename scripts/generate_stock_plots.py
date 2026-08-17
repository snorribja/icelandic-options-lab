import matplotlib.pyplot as plt
import yfinance as yf

ICELANDIC_STOCKS = {
    # Nasdaq Iceland Main Market
    "ALVO.IC": "Alvotech",
    "AMRQ.IC": "Amaroq",
    "ARION.IC": "Arion banki",
    "BERA.IC": "Bera",
    "BRIM.IC": "Brim",
    "EIK.IC": "Eik fasteignafélag",
    "EIM.IC": "Eimskipafélag Íslands",
    "FESTI.IC": "Festi",
    "HAGA.IC": "Hagar",
    "HAMP.IC": "Hampiðjan",
    "HEIMAR.IC": "Heimar",
    "ICEAIR.IC": "Icelandair Group",
    "ICESEA.IC": "Iceland Seafood International",
    "ISB.IC": "Íslandsbanki",
    "ISF.IC": "Ísfélag",
    "JBTM.IC": "JBT Marel",
    "KALD.IC": "Kaldalón",
    "KVIKA.IC": "Kvika banki",
    "NOVA.IC": "Nova Klúbburinn",
    "OCS.IC": "Oculis Holding",
    "REITIR.IC": "Reitir fasteignafélag",
    "SIMINN.IC": "Síminn",
    "SJOVA.IC": "Sjóvá",
    "SKAGI.IC": "Skagi",
    "SKEL.IC": "Skel fjárfestingafélag",
    "SVN.IC": "Síldarvinnslan",
    "SYN.IC": "Sýn",
}

output_path = "reports/figures/stocks/"

for stock_name, company_name in list(ICELANDIC_STOCKS.items()):
    plot_name = output_path + stock_name[:-2] + "svg"
    stock_ticker = yf.Ticker(stock_name)
    raw_stock_history = stock_ticker.history(period="max", auto_adjust=False)
    adj_stock_history = stock_ticker.history(period="max", auto_adjust=True)
    plt.plot(raw_stock_history.index, raw_stock_history["Close"], alpha=0.6, label="Raw")
    plt.plot(adj_stock_history.index, adj_stock_history["Close"], alpha=0.6, label="Adj")
    plt.legend()
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.grid(True)
    plt.title(f"{company_name} - Stock price trajectory")
    plt.savefig(plot_name)
    plt.close()
