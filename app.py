import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# Function to calculate RSI
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=window).mean()
    avg_loss = pd.Series(loss).rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Function to plot candlestick chart
def plot_candlestick(df):
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'],
                                         name='Candlestick')])
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name='MA20', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name='MA50', line=dict(color='orange')))
    fig.update_layout(title=f"{stock} Price Chart", xaxis_rangeslider_visible=False)
    return fig

# Streamlit UI
st.set_page_config(page_title="Real-Time Stock Dashboard", layout="wide")
st.title("📈 Real-Time Stock Price Dashboard")

stock = st.text_input("Enter Stock Symbol", "AAPL")
period = st.selectbox("Select Period", ["1mo", "3mo", "6mo", "1y"], index=2)
interval = st.selectbox("Select Interval", ["1d", "1wk", "1mo"], index=0)

if stock:
    df = yf.download(stock, period=period, interval=interval)
    if not df.empty:
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['Volatility'] = df['Close'].rolling(window=20).std()
        df['RSI'] = calculate_rsi(df)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.plotly_chart(plot_candlestick(df), use_container_width=True)
        with col2:
            st.metric(label="Latest Close", value=f"${df['Close'].iloc[-1]:.2f}")
            st.metric(label="Volatility (20-day)", value=f"{df['Volatility'].iloc[-1]:.2f}")
            st.metric(label="RSI (14-day)", value=f"{df['RSI'].iloc[-1]:.2f}")

        st.subheader("Recent Data Table")
        st.dataframe(df.tail(20))
    else:
        st.error("No data found. Please check the stock symbol.")
