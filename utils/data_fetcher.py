import yfinance as yf
import pandas as pd

def fetch_data(ticker, period="1y"):
    """
    Fetch historical daily adjusted close prices for a given ticker.
    Returns a Series of adjusted close prices.
    """
    data = yf.download(
        ticker,
        period=period,
        auto_adjust=False,
        progress=False
    )

    if data.empty:
        raise ValueError(f"No data found for {ticker}")

    # Prefer Adjusted Close if available
    if "Adj Close" in data.columns:
        prices = data["Adj Close"]
    else:
        prices = data["Close"]

    return prices.dropna()