import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# Streamlit application
st.set_page_config(page_title="Finance Data Dashboard", layout="wide")
st.title('Finance Data Dashboard')

# Sidebar for data type selection
st.sidebar.header('Select Data Type')
data_type = st.sidebar.radio('Choose data type', ['Stock', 'Forex', 'ETF', 'Crypto'])

# Sidebar for chart template selection
st.sidebar.header('Select Chart Template')
chart_templates = ['Candlestick with MA', 'Line Chart', 'Moving Averages Only', 'OHLC Chart']
chart_template = st.sidebar.selectbox('Choose chart template', chart_templates)

# Date range selection
col1, col2 = st.sidebar.columns(2)
start_date = col1.date_input('Start date', pd.to_datetime('2023-01-01'))
end_date = col2.date_input('End date', pd.to_datetime('2024-07-30'))

# Function to create OHLC or Candlestick trace
def create_ohlc_candlestick(data, chart_type='ohlc'):
    if 'Open' in data.columns and 'High' in data.columns and 'Low' in data.columns and 'Close' in data.columns:
        if chart_type == 'ohlc':
            return go.Ohlc(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='OHLC')
        else:
            return go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Candlestick')
    else:
        st.error("Data does not have required columns for Candlestick or OHLC charts.")
        return go.Figure()

# Function to calculate moving averages
def add_moving_averages(data, short_window, long_window):
    data['Short_MA'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
    data['Long_MA'] = data['Close'].rolling(window=long_window, min_periods=1).mean()

if data_type == 'Stock':
    # Expanded stock selection
    stocks = {
        'Google': 'GOOGL',
        'Apple': 'AAPL',
        'Microsoft': 'MSFT',
        'Amazon': 'AMZN',
        'Nvidia': 'NVDA',
        'Meta': 'META'
    }
    stock = st.sidebar.selectbox('Choose a stock', list(stocks.keys()))
    ticker = stocks[stock]

    # Fetch stock data
    data = yf.download(ticker, start=start_date, end=end_date)

    # Moving averages
    if chart_template in ['Candlestick with MA', 'Moving Averages Only']:
        st.sidebar.header('Moving Averages')
        short_window = st.sidebar.slider('Short window (days)', 5, 50, 20)
        long_window = st.sidebar.slider('Long window (days)', 50, 200, 100)

        # Calculate moving averages
        add_moving_averages(data, short_window, long_window)

    # Plotting stock data
    st.header(f'{stock} Stock Chart')
    fig = go.Figure()

    if chart_template == 'Candlestick with MA':
        fig.add_trace(create_ohlc_candlestick(data, 'candlestick'))
        fig.add_trace(go.Scatter(x=data.index, y=data['Short_MA'], mode='lines', name=f'Short {short_window}-day MA', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=data.index, y=data['Long_MA'], mode='lines', name=f'Long {long_window}-day MA', line=dict(color='red')))

    elif chart_template == 'Line Chart':
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'))

    elif chart_template == 'Moving Averages Only':
        fig.add_trace(go.Scatter(x=data.index, y=data['Short_MA'], mode='lines', name=f'Short {short_window}-day MA', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=data.index, y=data['Long_MA'], mode='lines', name=f'Long {long_window}-day MA', line=dict(color='red')))

    elif chart_template == 'OHLC Chart':
        fig.add_trace(create_ohlc_candlestick(data, 'ohlc'))

elif data_type == 'Forex':
    # Expanded forex selection
    forex_pairs = {
        'USD/EUR': 'EURUSD=X',
        'USD/JPY': 'JPY=X',
        'GBP/USD': 'GBPUSD=X',
        'USD/CHF': 'CHF=X',
        'AUD/USD': 'AUDUSD=X',
        'USD/CAD': 'CAD=X',
        'NZD/USD': 'NZDUSD=X',
        'USD/SGD': 'SGD=X'
    }
    forex_pair = st.sidebar.selectbox('Choose a forex pair', list(forex_pairs.keys()))
    ticker = forex_pairs[forex_pair]

    # Fetch forex data
    data = yf.download(ticker, start=start_date, end=end_date)

    # Moving averages
    if chart_template == 'Moving Averages Only':
        st.sidebar.header('Moving Averages')
        short_window = st.sidebar.slider('Short window (days)', 5, 50, 20)
        long_window = st.sidebar.slider('Long window (days)', 50, 200, 100)

        # Calculate moving averages
        add_moving_averages(data, short_window, long_window)

    # Plotting forex data
    st.header(f'{forex_pair} Forex Chart')
    fig = go.Figure()

    if chart_template == 'Line Chart':
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'))
    elif chart_template == 'OHLC Chart':
        fig.add_trace(create_ohlc_candlestick(data, 'ohlc'))
    elif chart_template == 'Moving Averages Only':
        fig.add_trace(go.Scatter(x=data.index, y=data['Short_MA'], mode='lines', name=f'Short {short_window}-day MA', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=data.index, y=data['Long_MA'], mode='lines', name=f'Long {long_window}-day MA', line=dict(color='red')))

elif data_type == 'ETF':
    # Expanded ETF selection
    etfs = {
        'SPDR S&P 500 ETF Trust': 'SPY',
        'Invesco QQQ Trust': 'QQQ',
        'iShares Russell 2000 ETF': 'IWM',
        'iShares MSCI Emerging Markets ETF': 'EEM',
        'Vanguard Total Stock Market ETF': 'VTI'
    }
    etf = st.sidebar.selectbox('Choose an ETF', list(etfs.keys()))
    ticker = etfs[etf]

    # Fetch ETF data
    data = yf.download(ticker, start=start_date, end=end_date)

    # Moving averages
    if chart_template in ['Candlestick with MA', 'Moving Averages Only']:
        st.sidebar.header('Moving Averages')
        short_window = st.sidebar.slider('Short window (days)', 5, 50, 20)
        long_window = st.sidebar.slider('Long window (days)', 50, 200, 100)

        # Calculate moving averages
        add_moving_averages(data, short_window, long_window)

    # Plotting ETF data
    st.header(f'{etf} ETF Chart')
    fig = go.Figure()

    if chart_template == 'Candlestick with MA':
        fig.add_trace(create_ohlc_candlestick(data, 'candlestick'))
        fig.add_trace(go.Scatter(x=data.index, y=data['Short_MA'], mode='lines', name=f'Short {short_window}-day MA', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=data.index, y=data['Long_MA'], mode='lines', name=f'Long {long_window}-day MA', line=dict(color='red')))

    elif chart_template == 'Line Chart':
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'))

    elif chart_template == 'Moving Averages Only':
        fig.add_trace(go.Scatter(x=data.index, y=data['Short_MA'], mode='lines', name=f'Short {short_window}-day MA', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=data.index, y=data['Long_MA'], mode='lines', name=f'Long {long_window}-day MA', line=dict(color='red')))

    elif chart_template == 'OHLC Chart':
        fig.add_trace(create_ohlc_candlestick(data, 'ohlc'))

elif data_type == 'Crypto':
    # Expanded crypto selection
    cryptos = {
        'Bitcoin': 'BTC-USD',
        'Ethereum': 'ETH-USD',
        'Ripple': 'XRP-USD',
        'Litecoin': 'LTC-USD',
        'Bitcoin Cash': 'BCH-USD'
    }
    crypto = st.sidebar.selectbox('Choose a cryptocurrency', list(cryptos.keys()))
    ticker = cryptos[crypto]

    # Fetch crypto data
    data = yf.download(ticker, start=start_date, end=end_date)

    # Moving averages
    if chart_template in ['Candlestick with MA', 'Moving Averages Only']:
        st.sidebar.header('Moving Averages')
        short_window = st.sidebar.slider('Short window (days)', 5, 50, 20)
        long_window = st.sidebar.slider('Long window (days)', 50, 200, 100)

        # Calculate moving averages
        add_moving_averages(data, short_window, long_window)

    # Plotting crypto data
    st.header(f'{crypto} Crypto Chart')
    fig = go.Figure()

    if chart_template == 'Candlestick with MA':
        fig.add_trace(create_ohlc_candlestick(data, 'candlestick'))
        fig.add_trace(go.Scatter(x=data.index, y=data['Short_MA'], mode='lines', name=f'Short {short_window}-day MA', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=data.index, y=data['Long_MA'], mode='lines', name=f'Long {long_window}-day MA', line=dict(color='red')))

    elif chart_template == 'Line Chart':
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'))

    elif chart_template == 'Moving Averages Only':
        fig.add_trace(go.Scatter(x=data.index, y=data['Short_MA'], mode='lines', name=f'Short {short_window}-day MA', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=data.index, y=data['Long_MA'], mode='lines', name=f'Long {long_window}-day MA', line=dict(color='red')))

    elif chart_template == 'OHLC Chart':
        fig.add_trace(create_ohlc_candlestick(data, 'ohlc'))

# Customize layout
fig.update_layout(
    title=f'{stock if data_type == "Stock" else forex_pair if data_type == "Forex" else etf if data_type == "ETF" else crypto} {"Stock Price" if data_type == "Stock" else "Exchange Rate" if data_type == "Forex" else "Price" if data_type == "ETF" else "Price"}',
    xaxis_title='Date',
    yaxis_title='Price' if data_type in ['Stock', 'ETF', 'Crypto'] else 'Exchange Rate',
    xaxis_rangeslider_visible=False,
    template='plotly_dark',
    height=600
)

# Display chart
st.plotly_chart(fig, use_container_width=True)

# Display data table
if st.checkbox('Show raw data'):
    st.write(data)
