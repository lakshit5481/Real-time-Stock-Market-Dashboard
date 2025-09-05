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

# --------- RESOURCES ----------
@st.cache_resource(show_spinner=False)
def get_http_session():
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0"})
    return s  # pooled connections

# --------- YAHOO FINANCE SEARCH WITH RETRIES ----------
@st.cache_data(show_spinner=False, ttl=3600, max_entries=512)
def search_ticker(company_name: str, max_retries=3):
    """Search company name and return the ticker symbol with retry logic."""
    session = get_http_session()
    backoff = 0.5
    for attempt in range(max_retries):
        try:
            url = "https://query2.finance.yahoo.com/v1/finance/search"
            resp = session.get(url, params={"q": company_name}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("quotes"):
                    for q in data["quotes"]:
                        sym = q.get("symbol")
                        if sym:
                            return sym
                return None
            time.sleep(backoff)
            backoff = min(backoff * 2, 4)
        except requests.RequestException:
            time.sleep(backoff)
            backoff = min(backoff * 2, 4)
    return None

# --------- FETCH STOCK DATA WITH ROBUST FALLBACKS ----------
@st.cache_data(show_spinner=False, ttl=120, max_entries=256)
def get_stock_data(symbol: str, period="1mo"):
    """
    Fetch historical stock data with robust interval fallbacks.
    - 5d: try 15m, then 30m, 60m, 1h
    - 1y: try 1wk, then 1d
    - 5y: try 1mo, then 1wk
    - max: try 3mo, then 1mo
    Others default to 1d.
    """
    try:
        interval_candidates_by_period = {
            "5d": ["15m", "30m", "60m", "1h"],
            "1mo": ["1d"],
            "3mo": ["1d"],
            "6mo": ["1d"],
            "1y": ["1wk", "1d"],
            "5y": ["1mo", "1wk"],
            "max": ["3mo", "1mo"],
        }
        intervals = interval_candidates_by_period.get(period, ["1d"])

        last_interval = None
        for interval in intervals:
            last_interval = interval
            df = yf.download(
                symbol,
                period=period,
                interval=interval,
                auto_adjust=True,
                progress=False,
                threads=True,
            )
            df = df.dropna()
            if df.empty:
                continue

            # Normalize datetime index for Altair/Streamlit plotting
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index, utc=True, errors="coerce")
            if isinstance(df.index, pd.DatetimeIndex) and df.index.tz is not None:
                df.index = df.index.tz_convert("UTC").tz_localize(None)

            df = df.reset_index().rename(columns={df.columns: "Date"})
            return df, interval

        return pd.DataFrame(), last_interval
    except Exception:
        return pd.DataFrame(), None

# --------- UI ----------
st.title("📊 Real-Time Stock Market Dashboard")
st.markdown("Track live **stock prices, volume, and trends** for any company.")

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
    st.caption("Data cached ~120s for responsiveness. 5d uses 15m with fallbacks; 1y uses 1wk→1d.")

if company_name:
    with st.spinner("Searching ticker symbol..."):
        if ticker_symbol_override:
            ticker = ticker_symbol_override
        else:
            ticker = search_ticker(company_name.strip())

    if ticker:
        st.subheader(f"📌 {company_name} ({ticker}) — Period: {time_period}")

        # IMPORTANT: ensure full function name is called; avoid NameError
        with st.spinner("Downloading stock data..."):
            df, interval_used = get_stock_data(ticker, period=time_period)

        if not df.empty:
            st.caption(f"✅ Data fetched (interval = {interval_used})")

            base = alt.Chart(df).encode(
                x=alt.X("Date:T", title="Date")  # explicit temporal encoding
            )

            close_chart = (
                base.mark_line(color="#1f77b4")
                .encode(
                    y=alt.Y("Close:Q", title="Closing Price ($)"),
                    tooltip=[alt.Tooltip("Date:T"), alt.Tooltip("Close:Q", format=".2f")]
                )
                .properties(title="Closing Price Over Time", height=300)
                .interactive()
            )

            volume_chart = (
                base.mark_bar(color="#ff7f0e")
                .encode(
                    y=alt.Y("Volume:Q", title="Volume"),
                    tooltip=[alt.Tooltip("Date:T"), alt.Tooltip("Volume:Q", format=",.0f")]
                )
                .properties(title="Volume Over Time", height=300)
                .interactive()
            )

            col1, col2 = st.columns(2)
            col1.altair_chart(close_chart, use_container_width=True)
            col2.altair_chart(volume_chart, use_container_width=True)

            st.divider()
            st.write("📅 **Latest Stock Data**")
            st.dataframe(df.tail(), use_container_width=True)
        else:
            st.error(
                f"No stock data available for {ticker} "
                f"(Period: {time_period}, Interval tried: {interval_used}). "
                "Try a longer period or check if the market is closed."
            )
    else:
        st.error(
            "❌ No ticker found for the entered company name.\n\n"
            "Try:\n"
            "- Using an exact company name (e.g., 'Tesla Inc').\n"
            "- Entering the known ticker symbol directly (e.g., 'TSLA').\n"
            "- Selecting a company from the dropdown list."
        )
else:
    st.info("Enter a company name or select one in the sidebar to get started.")
