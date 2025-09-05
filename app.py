import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import altair as alt
import time
import numpy as np

# --------- CONFIGURE PAGE ---------
st.set_page_config(
    page_title="📈 Real-Time Stock Dashboard",
    page_icon="📊",
    layout="wide"
)

# --------- POPULAR COMPANIES ----------
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

# --------- YAHOO FINANCE SEARCH ----------
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
                    return None
            else:
                attempt += 1
                time.sleep(1)
        except requests.RequestException:
            attempt += 1
            time.sleep(1)
    return None

# --------- FETCH STOCK DATA ----------
@st.cache_data(show_spinner=False)
def get_stock_data(symbol: str, period="1mo"):
    """Fetch historical stock data with indicators."""
    try:
        df = yf.download(symbol, period=period)
        df = df.dropna()

        # Technical Indicators
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()

        # Bollinger Bands
        df['BB_mid'] = df['Close'].rolling(window=20).mean()
        df['BB_std'] = df['Close'].rolling(window=20).std()
        df['BB_upper'] = df['BB_mid'] + (2 * df['BB_std'])
        df['BB_lower'] = df['BB_mid'] - (2 * df['BB_std'])

        # RSI (14)
        delta = df['Close'].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(window=14).mean()
        avg_loss = pd.Series(loss).rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))

        return df
    except Exception:
        return pd.DataFrame()

# --------- UI ----------
st.title("📊 Real-Time Stock Market Dashboard")
st.markdown("Track live **stock prices, indicators, and trends** for any company.")

with st.sidebar:
    st.header("🔍 Search Settings")
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
            df_reset = df.reset_index()

            # -------- Closing Price + MAs + Bollinger Bands --------
            price_chart = (
                alt.Chart(df_reset)
                .mark_line(color="blue")
                .encode(x="Date:T", y="Close:Q", tooltip=["Date:T", "Close:Q"])
                .properties(title="Closing Price + Moving Averages & Bollinger Bands", height=350)
            )
            ma20 = alt.Chart(df_reset).mark_line(color="orange").encode(x="Date:T", y="MA20:Q")
            ma50 = alt.Chart(df_reset).mark_line(color="green").encode(x="Date:T", y="MA50:Q")
            bb_upper = alt.Chart(df_reset).mark_line(color="gray").encode(x="Date:T", y="BB_upper:Q")
            bb_lower = alt.Chart(df_reset).mark_line(color="gray").encode(x="Date:T", y="BB_lower:Q")

            # Combine all
            price_final = price_chart + ma20 + ma50 + bb_upper + bb_lower

            # -------- RSI Chart --------
            rsi_chart = (
                alt.Chart(df_reset)
                .mark_line(color="purple")
                .encode(x="Date:T", y="RSI:Q", tooltip=["Date:T", "RSI:Q"])
                .properties(title="Relative Strength Index (RSI)", height=150)
            ).interactive()

            # -------- Layout --------
            st.altair_chart(price_final.interactive(), use_container_width=True)
            st.altair_chart(rsi_chart, use_container_width=True)

            # -------- Volume --------
            volume_chart = (
                alt.Chart(df_reset)
                .mark_bar(color="orange")
                .encode(x="Date:T", y="Volume:Q", tooltip=["Date:T", "Volume:Q"])
                .properties(title="Volume Over Time", height=200)
            )
            st.altair_chart(volume_chart.interactive(), use_container_width=True)

            # -------- Data Table --------
            st.divider()
            st.write("📅 **Latest Stock Data**")
            st.dataframe(df.tail(), use_container_width=True)

        else:
            st.error("No stock data available for this ticker symbol.")
    else:
        st.error("No ticker found for the entered company name.")
else:
    st.info("Enter a company name or select one in the sidebar to get started.")
