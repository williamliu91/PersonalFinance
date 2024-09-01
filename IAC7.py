import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# Streamlit application
st.set_page_config(page_title="Finance Data Dashboard", layout="wide")
st.title('Finance Data Dashboard')

# Sidebar for data type selection
st.sidebar.header('Select Data Type')
data_type = st.sidebar.radio('Choose data type', ['Stock', 'Forex', 'ETF', 'Crypto'])

# Sidebar for chart template selection
st.sidebar.header('Select Chart Template')
chart_templates = ['Candlestick with Indicators', 'Line Chart', 'OHLC Chart']
chart_template = st.sidebar.selectbox('Choose chart template', chart_templates)

# Date range selection
col1, col2 = st.sidebar.columns(2)
start_date = col1.date_input('Start date', pd.to_datetime('2023-01-01'))
end_date = col2.date_input('End date', pd.to_datetime('2024-08-31'))

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

# Function to calculate Bollinger Bands
def add_bollinger_bands(data, window=20, num_std=2):
    data['MA'] = data['Close'].rolling(window=window).mean()
    data['BB_upper'] = data['MA'] + (data['Close'].rolling(window=window).std() * num_std)
    data['BB_lower'] = data['MA'] - (data['Close'].rolling(window=window).std() * num_std)

# Function to calculate MACD
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    histogram = macd - signal
    return macd, signal, histogram

# Function to calculate Stochastic Oscillator
def calculate_stochastic(data, window=14, smooth_window=3):
    low_min = data['Low'].rolling(window=window).min()
    high_max = data['High'].rolling(window=window).max()
    k = 100 * ((data['Close'] - low_min) / (high_max - low_min))
    d = k.rolling(window=smooth_window).mean()
    return k, d

# Function to calculate Money Flow Index (MFI)
def calculate_mfi(data, period=14):
    typical_price = (data['High'] + data['Low'] + data['Close']) / 3
    money_flow = typical_price * data['Volume']
    positive_flow = pd.Series(np.where(typical_price > typical_price.shift(1), money_flow, 0), index=data.index)
    negative_flow = pd.Series(np.where(typical_price < typical_price.shift(1), money_flow, 0), index=data.index)
    
    positive_mf = positive_flow.rolling(window=period).sum()
    negative_mf = negative_flow.rolling(window=period).sum()
    
    mfi = 100 - (100 / (1 + positive_mf / negative_mf))
    return mfi


# Function to create and update the chart
def create_chart(data, title):
    # Moving averages
    st.sidebar.header('Moving Averages')
    short_window = st.sidebar.slider('Short window (days)', 5, 50, 20, key=f"{title}_short_ma")
    long_window = st.sidebar.slider('Long window (days)', 50, 200, 100, key=f"{title}_long_ma")

    # Calculate moving averages
    add_moving_averages(data, short_window, long_window)

    # RSI
    st.sidebar.header('RSI')
    rsi_window = st.sidebar.slider('RSI window (days)', 5, 30, 14, key=f"{title}_rsi")
    data['RSI'] = calculate_rsi(data, rsi_window)

    # Bollinger Bands
    st.sidebar.header('Bollinger Bands')
    bb_window = st.sidebar.slider('Bollinger Bands window (days)', 5, 50, 20, key=f"{title}_bb")
    bb_std = st.sidebar.slider('Number of standard deviations', 1, 3, 2, key=f"{title}_bb_std")
    add_bollinger_bands(data, bb_window, bb_std)

    # Add checkboxes for additional indicators
    st.sidebar.header('Additional Indicators')
    show_rsi = st.sidebar.checkbox('Show RSI', value=True)
    show_macd = st.sidebar.checkbox('Show MACD', value=False)
    show_stochastic = st.sidebar.checkbox('Show Stochastic Oscillator', value=False)
    show_mfi = st.sidebar.checkbox('Show MFI', value=False)
  

    # Calculate additional indicators if selected
    if show_macd:
        data['MACD'], data['Signal'], data['Histogram'] = calculate_macd(data)
    if show_stochastic:
        data['Stochastic_K'], data['Stochastic_D'] = calculate_stochastic(data)
    if show_mfi:
        data['MFI'] = calculate_mfi(data)


    # Determine the number of subplots
    num_subplots = 2  # Main chart and Volume
    if show_rsi:
        num_subplots += 1
    if show_macd:
        num_subplots += 1
    if show_stochastic:
        num_subplots += 1
    if show_mfi:
        num_subplots += 1
    

    # Create subplots
    fig = make_subplots(rows=num_subplots, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05,
                        row_heights=[0.5] + [0.5/(num_subplots-1)]*(num_subplots-1))

    # Main chart
    if chart_template == 'Candlestick with Indicators':
        fig.add_trace(create_ohlc_candlestick(data, 'candlestick'), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Short_MA'], mode='lines', name=f'Short {short_window}-day MA', line=dict(color='blue')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Long_MA'], mode='lines', name=f'Long {long_window}-day MA', line=dict(color='red')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['BB_upper'], mode='lines', name='Upper BB', line=dict(color='gray', dash='dash')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['BB_lower'], mode='lines', name='Lower BB', line=dict(color='gray', dash='dash')), row=1, col=1)
    elif chart_template == 'Line Chart':
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'), row=1, col=1)
    elif chart_template == 'OHLC Chart':
        fig.add_trace(create_ohlc_candlestick(data, 'ohlc'), row=1, col=1)

    # Volume subplot
    fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name='Volume', marker_color='blue'), row=2, col=1)

    current_row = 3

    # RSI subplot
    if show_rsi:
        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', line=dict(color='purple')), row=current_row, col=1)
        fig.update_yaxes(title_text='RSI', row=current_row, col=1)
        current_row += 1

    # MACD subplot
    if show_macd:
        fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], mode='lines', name='MACD', line=dict(color='blue')), row=current_row, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Signal'], mode='lines', name='Signal', line=dict(color='orange')), row=current_row, col=1)
        fig.add_trace(go.Bar(x=data.index, y=data['Histogram'], name='Histogram', marker_color='gray'), row=current_row, col=1)
        fig.update_yaxes(title_text='MACD', row=current_row, col=1)
        current_row += 1

    # Stochastic Oscillator subplot
    if show_stochastic:
        fig.add_trace(go.Scatter(x=data.index, y=data['Stochastic_K'], mode='lines', name='Stochastic %K', line=dict(color='blue')), row=current_row, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Stochastic_D'], mode='lines', name='Stochastic %D', line=dict(color='red')), row=current_row, col=1)
        fig.update_yaxes(title_text='Stochastic', row=current_row, col=1)
        current_row += 1

    # MFI subplot
    if show_mfi:
        fig.add_trace(go.Scatter(x=data.index, y=data['MFI'], mode='lines', name='MFI', line=dict(color='green')), row=current_row, col=1)
        fig.update_yaxes(title_text='MFI', row=current_row, col=1)
        current_row += 1


    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='Volumn',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        height=250 * num_subplots  # Adjust height based on number of subplots
    )

    return fig


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
    
    # Create and display the chart
    fig = create_chart(data, f'{stock} Stock')
    st.plotly_chart(fig, use_container_width=True)

elif data_type == 'Forex':
    forex_pairs = {
        'EUR/USD': 'EURUSD=X',
        'USD/JPY': 'JPY=X',
        'GBP/USD': 'GBPUSD=X',
        'USD/CHF': 'CHF=X',
        'AUD/USD': 'AUDUSD=X',
        'USD/CAD': 'CAD=X'
    }
    forex_pair = st.sidebar.selectbox('Choose a forex pair', list(forex_pairs.keys()))
    ticker = forex_pairs[forex_pair]

    # Fetch forex data
    data = yf.download(ticker, start=start_date, end=end_date)
    
    # Create and display the chart
    fig = create_chart(data, f'{forex_pair} Forex')
    st.plotly_chart(fig, use_container_width=True)

elif data_type == 'ETF':
    etfs = {
        'SPY (S&P 500)': 'SPY',
        'QQQ (Nasdaq 100)': 'QQQ',
        'DIA (Dow Jones)': 'DIA',
        'IWM (Russell 2000)': 'IWM',
        'VTI (Total Stock Market)': 'VTI',
        'GLD (Gold)': 'GLD'
    }
    etf = st.sidebar.selectbox('Choose an ETF', list(etfs.keys()))
    ticker = etfs[etf]

    # Fetch ETF data
    data = yf.download(ticker, start=start_date, end=end_date)
    
    # Create and display the chart
    fig = create_chart(data, f'{etf} ETF')
    st.plotly_chart(fig, use_container_width=True)

elif data_type == 'Crypto':
    cryptos = {
        'Bitcoin': 'BTC-USD',
        'Ethereum': 'ETH-USD',
        'Cardano': 'ADA-USD',
        'Dogecoin': 'DOGE-USD',
        'Ripple': 'XRP-USD',
        'Litecoin': 'LTC-USD'
    }
    crypto = st.sidebar.selectbox('Choose a cryptocurrency', list(cryptos.keys()))
    ticker = cryptos[crypto]

    # Fetch cryptocurrency data
    data = yf.download(ticker, start=start_date, end=end_date)
    
    # Create and display the chart
    fig = create_chart(data, f'{crypto} Cryptocurrency')
    st.plotly_chart(fig, use_container_width=True)