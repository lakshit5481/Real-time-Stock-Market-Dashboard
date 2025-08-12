import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import altair as alt

# --------- CONFIGURE PAGE ---------
st.set_page_config(
    page_title="📈 Real-Time Stock Dashboard",
    page_icon="📊",
    layout="wide"
)

# --------- YAHOO FINANCE SEARCH ----------
@st.cache_data(show_spinner=False)
def search_ticker(company_name: str):
    """Search company name and return the ticker symbol."""
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={company_name}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("quotes"):
                return data["quotes"][0]["symbol"]
        return None
    except requests.RequestException:
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
    company_name = st.text_input("Enter Company Name", "Tesla", placeholder="e.g., Apple, Google")
    time_period = st.selectbox(
        "Select Time Period",
        ["5d", "1mo", "3mo", "6mo", "1y", "5y", "max"],
        index=1
    )

if company_name:
    with st.spinner("Fetching ticker symbol..."):
        ticker = search_ticker(company_name)
    
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
            st.error("No stock data found for this company.")
    else:
        st.error("No ticker found. Try another company name.")
else:
    st.info("Enter a company name in the **sidebar** to get started.")
