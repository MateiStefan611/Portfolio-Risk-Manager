import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from utils.data_fetcher import fetch_data
from utils.returns import calculate_daily_returns
from utils.technical import calculate_rsi
from utils.fundamentals import fetch_fundamentals

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Portfolio Risk Manager", layout="centered")
st.title("📊 Portfolio Risk Manager")

tab1, tab2, tab3 = st.tabs(["📊 Portfolio Risk", "📈 Technical", "🏦 Fundamentals"])

# =========================
# INPUT SECTION
# =========================
st.markdown(
    "<p style='color: #2E8B57; font-weight: bold; font-size:18px;'>Enter tickers (e.g., AAPL, MSFT, TSLA)</p>",
    unsafe_allow_html=True
)
tickers_input = st.text_input("Tickers", "NVDA")

st.markdown(
    "<p style='color: #2E8B57; font-weight: bold; font-size:18px;'>Enter weights (sum must equal 1, e.g., 0.4,0.4,0.2)</p>",
    unsafe_allow_html=True
)
weights_input = st.text_input("Weights", "1")

period = st.selectbox(
    "Select historical data period for risk calculations:",
    ["1y", "3y", "5y", "10y"],
    index=2  # default 5y
)

# =========================
# TAB FUNCTIONS
# =========================
def portfolio_risk_tab(tickers, weights):

    all_returns = pd.DataFrame()

    with st.expander("ℹ️ What do these metrics mean and how are they calculated?"):
        st.markdown("""
        **Annualized Volatility** – measures portfolio risk:
        $$\\sigma_p = \\sqrt{w^T \\cdot Cov(R) \\cdot w} \\cdot \\sqrt{252}$$

        **Annualized Return** – average yearly portfolio return:
        $$R_{annual} = \\bar{R}_{daily} \\cdot 252$$

        **Sharpe Ratio** – return per unit of risk:
        $$Sharpe = \\frac{R_{annual}}{\\sigma_p}$$
        """)

    for ticker in tickers:
        prices = fetch_data(ticker, period=period)
        daily_returns = calculate_daily_returns(prices)
        all_returns[ticker] = daily_returns

    cov_matrix = all_returns.cov()
    portfolio_volatility = np.sqrt(weights.T @ cov_matrix.values @ weights) * np.sqrt(252)
    portfolio_daily_return = (all_returns * weights).sum(axis=1)
    portfolio_annual_return = portfolio_daily_return.mean() * 252
    sharpe_ratio = portfolio_annual_return / portfolio_volatility

    st.subheader("📈 Portfolio Results")
    col1, col2, col3 = st.columns(3)
    col1.metric("Annualized Volatility", f"{portfolio_volatility:.4f}")
    col2.metric("Annualized Return", f"{portfolio_annual_return:.4f}")
    col3.metric("Sharpe Ratio", f"{sharpe_ratio:.4f}")

    if len(tickers) > 1:
        st.subheader("Correlation Heatmap")
        fig, ax = plt.subplots(figsize=(8, 5))
        corr_matrix = all_returns.corr()
        im = ax.imshow(corr_matrix, cmap="RdYlGn", vmin=-1, vmax=1)
        plt.colorbar(im, ax=ax)
        ax.set_xticks(range(len(tickers)))
        ax.set_yticks(range(len(tickers)))
        ax.set_xticklabels(tickers, fontsize=12)
        ax.set_yticklabels(tickers, fontsize=12)

        for i in range(len(tickers)):
            for j in range(len(tickers)):
                ax.text(j, i, f"{corr_matrix.iloc[i, j]:.2f}",
                        ha="center", va="center",
                        fontsize=11, fontweight="bold")

        ax.set_title("Correlation Matrix", fontsize=14)
        st.pyplot(fig)
    else:
        st.info("Add more tickers to display the correlation heatmap.")


def technical_tab(tickers):
    st.subheader("RSI Indicator")

    with st.expander("ℹ️ What is RSI and how is it interpreted?"):
        st.markdown("""
        RSI (Relative Strength Index) indicates whether an asset is overbought or oversold:
        - Range: 0–100
        - RSI > 70 → Overbought (possible downside correction)
        - RSI < 30 → Oversold (possible upward rebound)

        RSI Formula:
        $$RSI = 100 - \\frac{100}{1 + RS}$$
        where RS = average gains / average losses
        """)

    st.subheader("📉 Price Evolution")

    fig, ax = plt.subplots(figsize=(10, 4))
    for ticker in tickers:
        prices = fetch_data(ticker)
        prices_normalized = prices / prices.iloc[0] * 100
        ax.plot(prices_normalized, label=ticker)

    ax.set_title("Normalized Price Evolution (Base = 100)")
    ax.set_ylabel("Normalized Value")
    ax.set_xlabel("Date")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)
    st.pyplot(fig)

    st.subheader("📉 RSI Charts")

    for ticker in tickers:
        prices = fetch_data(ticker)
        rsi = calculate_rsi(prices)

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(rsi, label=f"RSI {ticker}")
        ax.axhline(70, color = "red",  linestyle="--", label="Overbought (70)")
        ax.axhline(30, color = "green", linestyle="--", label="Oversold (30)")

        ax.set_title(f"RSI - {ticker}")
        ax.set_ylabel("RSI Value")
        ax.set_xlabel("Date")
        ax.set_ylim(0, 100)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(loc="upper right")

        st.pyplot(fig)


def fundamentals_tab(tickers):
    st.subheader("Fundamental Indicators")

    with st.expander("ℹ️ Fundamental Indicator Explanations"):
        st.markdown("""
        **P/E (Price / Earnings)**:
        $$P/E = \\frac{Price}{EPS}$$

        **Forward P/E** – estimated P/E based on future earnings

        **PEG (Price/Earnings to Growth)**:
        $$PEG = \\frac{P/E}{Growth\\%}$$

        **Debt/Equity**:
        $$D/E = \\frac{Total Debt}{Equity}$$

        **Insider Ownership** – percentage of shares held by insiders

        **Profit Margin**:
        $$Profit Margin = \\frac{Net Income}{Revenue}$$

        **Market Cap**:
        $$Market Cap = Price \\times Shares Outstanding$$
        """)

    for ticker in tickers:
        st.markdown(f"### {ticker}")
        fundamentals = fetch_fundamentals(ticker)

        fundamentals_formatted = format_fundamentals(fundamentals)

        df = pd.DataFrame(
            fundamentals_formatted.items(),
            columns=["Indicator", "Value"]
        )
        df.index = df.index + 1
        st.dataframe(df)

        pe = fundamentals.get("trailingPE") or fundamentals.get("forwardPE")
        growth = (
            fundamentals.get("earningsGrowth") or
            fundamentals.get("revenueGrowth") or
            fundamentals.get("earningsQuarterlyGrowth")
        )

        if pe is None:
            st.warning("P/E unavailable — PEG cannot be calculated.")
        elif growth is None:
            st.warning("Growth data unavailable for this ticker in the current data source. You can try https://finviz.com")
        else:
            growth_percent = growth * 100
            if growth_percent <= 0:
                st.warning(f"Negative growth ({growth_percent:.2f}%) — PEG not meaningful.")
            else:
                peg_manual = pe / growth_percent
                col1, col2 = st.columns(2)
                col1.metric("P/E", round(pe, 2))
                col2.metric("Growth %", round(growth_percent, 2))
                st.metric("PEG (Manual)", round(peg_manual, 2))

                if peg_manual < 1:
                    st.success("✅ Possibly Undervalued")
                elif peg_manual <= 2:
                    st.info("➡️ Fairly Valued")
                else:
                    st.warning("⚠️ Possibly Overvalued")


DISPLAY_NAMES = {
    "trailingPE": "Trailing P/E",
    "forwardPE": "Forward P/E",
    "marketCap": "Market Cap",
    "profitMargin": "Profit Margin",
    "debtToEquity": "Debt / Equity",
    "earningsGrowth": "Earnings Growth",
    "totalRevenue": "Total Revenue",
    "netIncome": "Net Income",
    "insiderOwnership": "Insider Ownership",
}


def format_fundamentals(fundamentals):
    formatted = {}
    for key, value in fundamentals.items():
        display_name = DISPLAY_NAMES.get(key, key)

        if value is None:
            formatted[display_name] = "N/A"
        elif "cap" in key.lower() or "revenue" in key.lower() or "income" in key.lower():
            formatted[display_name] = f"${value/1e9:,.2f} B"
        elif "growth" in key.lower() or "margin" in key.lower() or "ownership" in key.lower():
            formatted[display_name] = f"{value*100:.2f}%"
        elif isinstance(value, (int, float)):
            formatted[display_name] = f"{value:,.2f}"
        else:
            formatted[display_name] = value

    return formatted


# =========================
# MAIN BUTTON
# =========================
if st.button("Calculate"):
    try:
        tickers = [t.strip().upper() for t in tickers_input.split(",")]
        weights = np.array([float(w) for w in weights_input.split(",")])

        if len(weights) != len(tickers):
            st.error("Number of weights must match number of tickers.")
        elif not np.isclose(weights.sum(), 1.0):
            st.error("Weights must sum to 1.")
        else:
            with tab1:
                portfolio_risk_tab(tickers, weights)
            with tab2:
                technical_tab(tickers)
            with tab3:
                fundamentals_tab(tickers)

    except Exception as e:
        st.error(f"Error: {e}")