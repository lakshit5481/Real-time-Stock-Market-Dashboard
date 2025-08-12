import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import altair as alt
import time

# --------- CONFIGURE PAGE ---------
st.set_page_config(
    page_title="📈 Real-Time Stock Dashboard",
    page_icon="📊",
    layout="wide"
)

# --------- POPULAR COMPANIES FOR QUICK SELECT ----------
POPULAR_COMPANIES = {
    "Apple Inc": "AAPL",
    "Microsoft Corporation": "MSFT",
    "Amazon.com Inc": "AMZN",
    "Tesla Inc": "TSLA",
    "Alphabet Inc": "GOOGL",
    "Meta Platforms Inc": "META",
    "NVIDIA Corporation": "NVDA",
    "Netflix Inc": "NFLX",
}

# --------- YAHOO FINANCE SEARCH WITH RETRIES ----------
@st.cache_data(show_spinner=False)
def search_ticker(company_name: str, max_retries=3):
    """Search company name and return the ticker symbol with retry logic."""
    attempt = 0
    while attempt < max_retries:
        try:
            url = f"https://query2.finance.yahoo.com/v1/finance/search?q={company_name}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("quotes"):
                    return data["quotes"][0]["symbol"]
                else:
                    # No ticker found
                    return None
            else:
                attempt += 1
                time.sleep(1)  # Small delay before retrying
        except requests.RequestException:
            attempt += 1
            time.sleep(1)
    return None

# --------- FETCH STOCK DATA ----------
@st.cache_data(show_spinner=False)
def get_stock_data(symbol: str, period="1mo"):
    """Fetch historical stock data."""
    try:
        df = yf.download(symbol, period=period)
        df = df.dropna()
        return df
    except Exception:
        return pd.DataFrame()

# --------- UI COMPONENTS ----------
st.title("📊 Real-Time Stock Market Dashboard")
st.markdown("Track live **stock prices, volume, and trends** for any company.")

with st.sidebar:
    st.header("🔍 Search Settings")

    # Provide a selectbox of popular companies with option for custom input
    option = st.selectbox(
        "Select a popular company or enter your own below",
        ["-- Select --"] + list(POPULAR_COMPANIES.keys())
    )
    if option != "-- Select --":
        company_name = option
        ticker_symbol_override = POPULAR_COMPANIES[option]
    else:
        company_name = st.text_input(
            "Enter Company Name or Ticker Symbol",
            placeholder="e.g., Tesla Inc or TSLA"
        )
        ticker_symbol_override = None

    time_period = st.selectbox(
        "Select Time Period",
        ["5d", "1mo", "3mo", "6mo", "1y", "5y", "max"],
        index=1
    )

if company_name:
    with st.spinner("Searching ticker symbol..."):
        if ticker_symbol_override:
            ticker = ticker_symbol_override
        else:
            ticker = search_ticker(company_name.strip())

    if ticker:
        st.subheader(f"📌 {company_name} ({ticker}) — Period: {time_period}")

        with st.spinner("Downloading stock data..."):
            df = get_stock_data(ticker, period=time_period)

        if not df.empty:
            # Close Price Chart
            close_chart = (
                alt.Chart(df.reset_index())
                .mark_line(color="#1f77b4")
                .encode(
                    x="Date:T",
                    y=alt.Y("Close:Q", title="Closing Price ($)"),
                    tooltip=["Date:T", "Close:Q"]
                )
                .properties(title="Closing Price Over Time", height=300)
                .interactive()
            )

            # Volume Chart
            volume_chart = (
                alt.Chart(df.reset_index())
                .mark_bar(color="#ff7f0e")
                .encode(
                    x="Date:T",
                    y=alt.Y("Volume:Q", title="Volume"),
                    tooltip=["Date:T", "Volume:Q"]
                )
                .properties(title="Volume Over Time", height=300)
                .interactive()
            )

            col1, col2 = st.columns(2)
            col1.altair_chart(close_chart, use_container_width=True)
            col2.altair_chart(volume_chart, use_container_width=True)

            # Show Latest Data
            st.divider()
            st.write("📅 **Latest Stock Data**")
            st.dataframe(df.tail(), use_container_width=True)
        else:
            st.error(
                "No stock data available for this ticker symbol. "
                "Try a different time period or company."
            )
    else:
        st.error(
            "No ticker found for the entered company name. "
            "Please try:\n"
            "- Using an exact company name (e.g., 'Tesla Inc').\n"
            "- Entering the known ticker symbol directly (e.g., 'TSLA').\n"
            "- Selecting a company from the dropdown list."
        )
else:
    st.info("Enter a company name or select one in the sidebar to get started.")
