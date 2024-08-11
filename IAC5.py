import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

# Function to calculate RSI
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Data fetching and plotting
if data_type == 'Stock':
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

    # RSI
    if chart_template in ['Candlestick with MA', 'Moving Averages Only', 'Line Chart']:
        st.sidebar.header('RSI')
        rsi_window = st.sidebar.slider('RSI window (days)', 5, 30, 14)
        data['RSI'] = calculate_rsi(data, rsi_window)

    # Create subplots
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=(f'{stock} Stock Chart', 'RSI'), vertical_spacing=0.15)

    # Main chart
    if chart_template == 'Candlestick with MA':
        fig.add_trace(create_ohlc_candlestick(data, 'candlestick'), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Short_MA'], mode='lines', name=f'Short {short_window}-day MA', line=dict(color='blue')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Long_MA'], mode='lines', name=f'Long {long_window}-day MA', line=dict(color='red')), row=1, col=1)

    elif chart_template == 'Line Chart':
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'), row=1, col=1)

    elif chart_template == 'Moving Averages Only':
        fig.add_trace(go.Scatter(x=data.index, y=data['Short_MA'], mode='lines', name=f'Short {short_window}-day MA', line=dict(color='blue')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Long_MA'], mode='lines', name=f'Long {long_window}-day MA', line=dict(color='red')), row=1, col=1)

    elif chart_template == 'OHLC Chart':
        fig.add_trace(create_ohlc_candlestick(data, 'ohlc'), row=1, col=1)

    # RSI subplot
    if chart_template in ['Candlestick with MA', 'Moving Averages Only', 'Line Chart']:
        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', line=dict(color='purple')), row=2, col=1)

    # Customize layout
    fig.update_layout(
        title=f'{stock} Stock Chart',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        height=800  # Total height of the figure
    )

    fig.update_yaxes(title_text='RSI', row=2, col=1)
    fig.update_layout(
        height=800,  # Total height of the figure
        yaxis2=dict(
            title='RSI',
            titlefont=dict(size=14),
            tickfont=dict(size=12),
            domain=[0, 0.2]  # Adjust the domain to allocate space for the RSI subplot
        ),
        yaxis=dict(
            title='Price',
            titlefont=dict(size=14),
            tickfont=dict(size=12),
            domain=[0.2, 1]  # Adjust the domain to allocate space for the main chart
        )
    )

elif data_type == 'Forex':
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
    fig = make_subplots(rows=1, cols=1, subplot_titles=[f'{forex_pair} Forex Chart'])

    if chart_template == 'Line Chart':
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'), row=1, col=1)
    elif chart_template == 'OHLC Chart':
        fig.add_trace(create_ohlc_candlestick(data, 'ohlc'), row=1, col=1)
    elif chart_template == 'Moving Averages Only':
        fig.add_trace(go.Scatter(x=data.index, y=data['Short_MA'], mode='lines', name=f'Short {short_window}-day MA', line=dict(color='blue')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Long_MA'], mode='lines', name=f'Long {long_window}-day MA', line=dict(color='red')), row=1, col=1)

    # Customize layout
    fig.update_layout(
        title=f'{forex_pair} Forex Chart',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        height=600  # Total height of the figure
    )

elif data_type == 'ETF':
    etfs = {
        'SPY': 'SPY',
        'IVV': 'IVV',
        'VTI': 'VTI',
        'XLF': 'XLF',
        'XLI': 'XLI',
        'XLB': 'XLB'
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

    # RSI
    if chart_template in ['Candlestick with MA', 'Moving Averages Only', 'Line Chart']:
        st.sidebar.header('RSI')
        rsi_window = st.sidebar.slider('RSI window (days)', 5, 30, 14)
        data['RSI'] = calculate_rsi(data, rsi_window)

    # Create subplots
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=(f'{etf} ETF Chart', 'RSI'), vertical_spacing=0.15)

    # Main chart
    if chart_template == 'Candlestick with MA':
        fig.add_trace(create_ohlc_candlestick(data, 'candlestick'), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Short_MA'], mode='lines', name=f'Short {short_window}-day MA', line=dict(color='blue')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Long_MA'], mode='lines', name=f'Long {long_window}-day MA', line=dict(color='red')), row=1, col=1)

    elif chart_template == 'Line Chart':
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'), row=1, col=1)

    elif chart_template == 'Moving Averages Only':
        fig.add_trace(go.Scatter(x=data.index, y=data['Short_MA'], mode='lines', name=f'Short {short_window}-day MA', line=dict(color='blue')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Long_MA'], mode='lines', name=f'Long {long_window}-day MA', line=dict(color='red')), row=1, col=1)

    elif chart_template == 'OHLC Chart':
        fig.add_trace(create_ohlc_candlestick(data, 'ohlc'), row=1, col=1)

    # RSI subplot
    if chart_template in ['Candlestick with MA', 'Moving Averages Only', 'Line Chart']:
        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', line=dict(color='purple')), row=2, col=1)

    # Customize layout
    fig.update_layout(
        title=f'{etf} ETF Chart',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        height=800  # Total height of the figure
    )

    fig.update_yaxes(title_text='RSI', row=2, col=1)
    fig.update_layout(
        height=800,  # Total height of the figure
        yaxis2=dict(
            title='RSI',
            titlefont=dict(size=14),
            tickfont=dict(size=12),
            domain=[0, 0.35]  # Adjust the domain to allocate space for the RSI subplot
        ),
        yaxis=dict(
            title='Price',
            titlefont=dict(size=14),
            tickfont=dict(size=12),
            domain=[0.35, 1]  # Adjust the domain to allocate space for the main chart
        )
    )

elif data_type == 'Crypto':
    cryptos = {
        'Bitcoin': 'BTC-USD',
        'Ethereum': 'ETH-USD',
        'Ripple': 'XRP-USD',
        'Litecoin': 'LTC-USD',
        'Cardano': 'ADA-USD'
    }
    crypto = st.sidebar.selectbox('Choose a cryptocurrency', list(cryptos.keys()))
    ticker = cryptos[crypto]

    # Fetch cryptocurrency data
    data = yf.download(ticker, start=start_date, end=end_date)

    # Moving averages
    if chart_template in ['Candlestick with MA', 'Moving Averages Only']:
        st.sidebar.header('Moving Averages')
        short_window = st.sidebar.slider('Short window (days)', 5, 50, 20)
        long_window = st.sidebar.slider('Long window (days)', 50, 200, 100)

        # Calculate moving averages
        add_moving_averages(data, short_window, long_window)

    # RSI
    if chart_template in ['Candlestick with MA', 'Moving Averages Only', 'Line Chart']:
        st.sidebar.header('RSI')
        rsi_window = st.sidebar.slider('RSI window (days)', 5, 30, 14)
        data['RSI'] = calculate_rsi(data, rsi_window)

    # Create subplots
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=(f'{crypto} Cryptocurrency Chart', 'RSI'), vertical_spacing=0.15)

    # Main chart
    if chart_template == 'Candlestick with MA':
        fig.add_trace(create_ohlc_candlestick(data, 'candlestick'), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Short_MA'], mode='lines', name=f'Short {short_window}-day MA', line=dict(color='blue')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Long_MA'], mode='lines', name=f'Long {long_window}-day MA', line=dict(color='red')), row=1, col=1)

    elif chart_template == 'Line Chart':
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'), row=1, col=1)

    elif chart_template == 'Moving Averages Only':
        fig.add_trace(go.Scatter(x=data.index, y=data['Short_MA'], mode='lines', name=f'Short {short_window}-day MA', line=dict(color='blue')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Long_MA'], mode='lines', name=f'Long {long_window}-day MA', line=dict(color='red')), row=1, col=1)

    elif chart_template == 'OHLC Chart':
        fig.add_trace(create_ohlc_candlestick(data, 'ohlc'), row=1, col=1)

    # RSI subplot
    if chart_template in ['Candlestick with MA', 'Moving Averages Only', 'Line Chart']:
        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', line=dict(color='purple')), row=2, col=1)

    # Customize layout
    fig.update_layout(
        title=f'{crypto} Cryptocurrency Chart',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        height=800  # Total height of the figure
    )

    fig.update_yaxes(title_text='RSI', row=2, col=1)
    fig.update_layout(
        height=800,  # Total height of the figure
        yaxis2=dict(
            title='RSI',
            titlefont=dict(size=14),
            tickfont=dict(size=12),
            domain=[0, 0.35]  # Adjust the domain to allocate space for the RSI subplot
        ),
        yaxis=dict(
            title='Price',
            titlefont=dict(size=14),
            tickfont=dict(size=12),
            domain=[0.35, 1]  # Adjust the domain to allocate space for the main chart
        )
    )

# Display the figure
st.plotly_chart(fig)
