import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# Search for ticker symbol by company name
def search_ticker(company_name):
    try:
        response = requests.get(
            f"https://query2.finance.yahoo.com/v1/finance/search?q={company_name}",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if "quotes" in data and data["quotes"]:
                return data["quotes"][0]["symbol"]
        return None
    except Exception as e:
        st.error(f"Error fetching ticker: {e}")
        return None

# Get stock data
def get_stock_data(symbol, period="1mo"):
    try:
        df = yf.download(symbol, period=period)
        if df is not None and not df.empty:
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        return pd.DataFrame()

st.title("📈 Real-Time Stock Market Dashboard")

company_name = st.text_input("Enter Company Name", "Tesla")
if company_name:
    ticker = search_ticker(company_name)
    if ticker:
        st.write(f"**Ticker Symbol:** {ticker}")

        df = get_stock_data(ticker)

        if not df.empty:
            # Closing price chart
            if "Close" in df.columns and not df["Close"].isna().all():
                st.subheader("Closing Price Over Time")
                st.line_chart(df["Close"])
            else:
                st.warning("No valid closing price data available.")

            # Volume chart
            if "Volume" in df.columns and not df["Volume"].isna().all():
                st.subheader("Volume Over Time")
                st.bar_chart(df["Volume"])
            else:
                st.warning("No valid volume data available.")
        else:
            st.error("No stock data found for this company.")
    else:
        st.error("No ticker found for the entered company name.")
