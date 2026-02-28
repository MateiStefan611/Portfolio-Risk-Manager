import pandas as pd

def calculate_daily_returns(prices: pd.Series) -> pd.Series:
    """
    Calculează randamentele zilnice (% change)
    """
    returns = prices.pct_change().dropna()
    return returns