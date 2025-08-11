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
            # Check for latest close
            if 'Close' in df and not df['Close'].isna().all():
                latest_close = df['Close'].iloc[-1]
            else:
                latest_close = None
            st.metric(label="Latest Close", value=f"${latest_close:.2f}" if latest_close is not None else "N/A")

            # Check for latest volatility
            if 'Volatility' in df and not df['Volatility'].isna().all():
                latest_volatility = df['Volatility'].iloc[-1]
            else:
                latest_volatility = None
            st.metric(label="Volatility (20-day)", value=f"{latest_volatility:.2f}" if latest_volatility is not None else "N/A")

            # Check for latest RSI
            if 'RSI' in df and not df['RSI'].isna().all():
                latest_rsi = df['RSI'].iloc[-1]
            else:
                latest_rsi = None
            st.metric(label="RSI (14-day)", value=f"{latest_rsi:.2f}" if latest_rsi is not None else "N/A")

        st.subheader("Recent Data Table")
        st.dataframe(df.tail(20))
    else:
        st.error("Not enough data to compute metrics. Try a longer period.")
else:
    st.error("No data found. Please check the stock symbol.")
