import yfinance as yf

def fetch_fundamentals(ticker):
    try:
        stock = yf.Ticker(ticker)

        try:
            info = stock.get_info()
        except:
            info = {}

        if not info:
            try:
                info = stock.info
            except:
                info = {}

        return {
            "trailingPE": info.get("trailingPE"),
            "forwardPE": info.get("forwardPE"),
            "marketCap": info.get("marketCap"),
            "profitMargin": info.get("profitMargins"),
            "debtToEquity": info.get("debtToEquity"),
            "earningsGrowth": info.get("earningsGrowth"),
            "totalRevenue": info.get("totalRevenue"),
            "netIncome": info.get("netIncomeToCommon"),
            "insiderOwnership": info.get("heldPercentInsiders"),
        }

    except Exception as e:
        print("EROARE fundamentals:", e)
        return {}