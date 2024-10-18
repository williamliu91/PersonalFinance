import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import base64


# Streamlit application
st.set_page_config(page_title="Stock Data Dashboard", layout="wide")
st.title('Stock Data Dashboard')

# Function to load the image and convert it to base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Path to the locally stored QR code image
qr_code_path = "qrcode.png"  # Ensure the image is in your app directory

# Convert image to base64
qr_code_base64 = get_base64_of_bin_file(qr_code_path)

# Custom CSS to position the QR code close to the top-right corner under the "Deploy" area
st.markdown(
    f"""
    <style>
    .qr-code {{
        position: fixed;  /* Keeps the QR code fixed in the viewport */
        top: 10px;       /* Sets the distance from the top of the viewport */
        right: 10px;     /* Sets the distance from the right of the viewport */
        width: 200px;    /* Adjusts the width of the QR code */
        z-index: 100;    /* Ensures the QR code stays above other elements */
    }}
    </style>
    <img src="data:image/png;base64,{qr_code_base64}" class="qr-code">
    """,
    unsafe_allow_html=True
)


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

# Function to generate trading signals
def generate_signals(data, rsi_buy_level, rsi_sell_level):
    # Ensure RSI thresholds are within a reasonable range
    rsi_buy_level = max(0, min(100, rsi_buy_level))
    rsi_sell_level = max(0, min(100, rsi_sell_level))
    
    # RSI Signal
    data['RSI_Signal'] = np.where((data['RSI'] < rsi_buy_level) & (rsi_buy_level < 100), 1, 
                                   np.where((data['RSI'] > rsi_sell_level) & (rsi_sell_level > 0), -1, 0))
  

    # Bollinger Bands Signal
    data['BB_Signal'] = np.where(data['Close'] < data['BB_lower'], 1, 
                                 np.where(data['Close'] > data['BB_upper'], -1, 0))
    
    # Combined Signal
    data['Combined_Signal'] = data['RSI_Signal'] + data['BB_Signal']

# Function to calculate Stochastic Oscillator
def calculate_stochastic(data, k_window=14, d_window=3):
    """
    Calculate Stochastic Oscillator %K and %D.

    :param data: DataFrame containing stock data.
    :param k_window: Window for %K calculation.
    :param d_window: Window for %D calculation.
    :return: Tuple of %K and %D values.
    """
    min_low = data['Low'].rolling(window=k_window).min()
    max_high = data['High'].rolling(window=k_window).max()
    
    # Calculate %K
    data['Stochastic_K'] = 100 * ((data['Close'] - min_low) / (max_high - min_low))
    
    # Calculate %D
    data['Stochastic_D'] = data['Stochastic_K'].rolling(window=d_window).mean()
    
    return data['Stochastic_K'], data['Stochastic_D']

# Function to calculate MACD
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    """
    Calculate the MACD and signal line.

    :param data: DataFrame containing stock data.
    :param short_window: Short window for MACD calculation.
    :param long_window: Long window for MACD calculation.
    :param signal_window: Signal window for MACD calculation.
    :return: Tuple of MACD, Signal line, and Histogram values.
    """
    # Calculate the short and long EMA
    short_ema = data['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()

    # Calculate MACD
    data['MACD'] = short_ema - long_ema
    data['Signal'] = data['MACD'].ewm(span=signal_window, adjust=False).mean()
    data['Histogram'] = data['MACD'] - data['Signal']

    return data['MACD'], data['Signal'], data['Histogram']

# Function to calculate MFI
def calculate_mfi(data, window=14):
    """
    Calculate the Money Flow Index (MFI).

    :param data: DataFrame containing stock data.
    :param window: Lookback period for MFI calculation.
    :return: MFI values.
    """
    # Calculate typical price
    typical_price = (data['High'] + data['Low'] + data['Close']) / 3

    # Calculate money flow
    data['Money_Flow'] = typical_price * data['Volume']

    # Calculate positive and negative money flow
    data['Positive_Flow'] = np.where(typical_price.diff(1) > 0, data['Money_Flow'], 0)
    data['Negative_Flow'] = np.where(typical_price.diff(1) < 0, data['Money_Flow'], 0)

    # Calculate MFI
    positive_flow_sum = data['Positive_Flow'].rolling(window=window).sum()
    negative_flow_sum = data['Negative_Flow'].rolling(window=window).sum()
    mfi = 100 - (100 / (1 + (positive_flow_sum / negative_flow_sum)))
    
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

    # Buy and Sell levels for RSI
    st.sidebar.header('RSI Buy/Sell Levels')
    rsi_buy_level = st.sidebar.slider('RSI Buy Level', 0, 50, 30)  # Default 30
    rsi_sell_level = st.sidebar.slider('RSI Sell Level', 50, 100, 70)  # Default 70

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

    # Generate trading signals
    generate_signals(data, rsi_buy_level, rsi_sell_level)

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
        
        # Add buy and sell signals
        buy_signals = data[data['Combined_Signal'] > 1]
        sell_signals = data[data['Combined_Signal'] < -1]
        fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Low'], mode='markers', name='Buy Signal', marker=dict(symbol='triangle-up', size=10, color='green')), row=1, col=1)
        fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['High'], mode='markers', name='Sell Signal', marker=dict(symbol='triangle-down', size=10, color='red')), row=1, col=1)
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
        
        # Add RSI threshold lines
        fig.add_trace(go.Scatter(x=data.index, y=[rsi_buy_level]*len(data), mode='lines', name='Buy Level', line=dict(color='green', dash='dash')), row=current_row, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=[rsi_sell_level]*len(data), mode='lines', name='Sell Level', line=dict(color='red', dash='dash')), row=current_row, col=1)
        
        fig.update_yaxes(title_text='RSI', row=current_row, col=1)
        current_row += 1

    # MACD subplot
    if show_macd:
        fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], mode='lines', name='MACD', line=dict(color='blue')), row=current_row, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Signal'], mode='lines', name='Signal', line=dict(color='red')), row=current_row, col=1)
        fig.update_yaxes(title_text='MACD', row=current_row, col=1)
        current_row += 1

    # Stochastic subplot
    if show_stochastic:
        fig.add_trace(go.Scatter(x=data.index, y=data['Stochastic_K'], mode='lines', name='Stochastic %K', line=dict(color='green')), row=current_row, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Stochastic_D'], mode='lines', name='Stochastic %D', line=dict(color='red')), row=current_row, col=1)
        fig.update_yaxes(title_text='Stochastic', row=current_row, col=1)
        current_row += 1

    # MFI subplot
    if show_mfi:
        fig.add_trace(go.Scatter(x=data.index, y=data['MFI'], mode='lines', name='MFI', line=dict(color='orange')), row=current_row, col=1)
        fig.update_yaxes(title_text='MFI', row=current_row, col=1)

    # Update layout
    fig.update_layout(title=title, xaxis_title='Date', xaxis_rangeslider_visible=False, height=300*num_subplots)

    # Display the figure
    st.plotly_chart(fig)

# Fetching the stock data
ticker = st.sidebar.text_input("Enter Stock Ticker", 'GOOGL').upper()
data = yf.download(ticker, start=start_date, end=end_date)
if not data.empty:
    create_chart(data, f'Stock Data for {ticker}')
else:
    st.error("No data found for this ticker.")
