import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

def calculate_rsi(data, window=14):
    if data.empty or 'Close' not in data:
        return pd.Series(dtype=float)
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def plot_candlestick(df, stock):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Candlestick')
    ])
    if 'MA20' in df:
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name='MA20', line=dict(color='blue')))
    if 'MA50' in df:
        fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name='MA50', line=dict(color='orange')))
    fig.update_layout(title=f"{stock} Price Chart", xaxis_rangeslider_visible=False)
    return fig

st.set_page_config(page_title="Real-Time Stock Dashboard", layout="wide")
st.title("📈 Real-Time Stock Price Dashboard")

# Initialize df as an empty DataFrame
df = pd.DataFrame()

# Sidebar for user inputs
st.sidebar.header("User  Input")
stock = st.sidebar.text_input("Enter Stock Symbol", "AAPL")
period = st.sidebar.selectbox("Select Period", ["1mo", "3mo", "6mo", "1y"], index=2)
interval = st.sidebar.selectbox("Select Interval", ["1d", "1wk", "1mo"], index=0)

if st.sidebar.button("Fetch Data"):
    with st.spinner("Fetching data..."):
        try:
            df = yf.download(stock, period=period, interval=interval, progress=False)
        except Exception as e:
            st.error(f"Error fetching data: {e}")
    
    if not df.empty:
        df.dropna(inplace=True)
        if len(df) >= 20:
            df['MA20'] = df['Close'].rolling(window=20, min_periods=1).mean()
            df['MA50'] = df['Close'].rolling(window=50, min_periods=1).mean()
            df['Volatility'] = df['Close'].rolling(window=20, min_periods=1).std()
            df['RSI'] = calculate_rsi(df)

            col1, col2 = st.columns([3, 1])
            with col1:
                st.plotly_chart(plot_candlestick(df, stock), use_container_width=True)
            with col2:
                latest_close = df['Close'].iloc[-1] if 'Close' in df and not df['Close'].isna().all() else None
                st.metric(label="Latest Close", value=f"${latest_close:.2f}" if latest_close is not None else "N/A")

                latest_volatility = df['Volatility'].iloc[-1] if 'Volatility' in df and not df['Volatility'].isna().all() else None
                st.metric(label="Volatility (20-day)", value=f"{latest_volatility:.2f}" if latest_volatility is not None else "N/A")

                latest_rsi = df['RSI'].iloc[-1] if 'RSI' in df and not df['RSI'].isna().all() else None
                st.metric(label="RSI (14-day)", value=f"{latest_rsi:.2f}" if latest_rsi is not None else "N/A")

            st.subheader("Recent Data Table")
            st.dataframe(df.tail(20))
        else:
            st.error("Not enough data to compute metrics. Try a longer period.")
    else:
        st.error("No data found. Please check the stock symbol.")
