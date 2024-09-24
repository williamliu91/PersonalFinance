import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Set up Streamlit app title
st.title('Top 100 Stock Trend Analysis with 200-Day SMA')

# Stock ticker selection
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'FB', 'TSLA', 'BRK-B', 'NVDA', 'JPM', 'JNJ',
    'V', 'PG', 'UNH', 'HD', 'MA', 'DIS', 'PYPL', 'NFLX', 'CMCSA', 'PEP',
    'VZ', 'T', 'MRK', 'INTC', 'CSCO', 'ABT', 'NKE', 'PFE', 'XOM', 'TMO',
    'ACN', 'IBM', 'CVX', 'LLY', 'PM', 'WMT', 'MDT', 'COST', 'AMGN', 'TXN',
    'AVGO', 'ADBE', 'IBM', 'QCOM', 'BMY', 'NOW', 'LMT', 'ISRG', 'SBUX', 'CAT',
    'HON', 'NEM', 'SYY', 'AMAT', 'ATVI', 'CHTR', 'GILD', 'ADI', 'SYK', 'FISV',
    'DHR', 'MMC', 'LRCX', 'SPGI', 'C', 'BA', 'ADP', 'CME', 'BIIB', 'MS',
    'ZTS', 'GS', 'NTRS', 'LHX', 'MET', 'SRE', 'KMB', 'ADSK', 'NTES', 'CDW',
    'CB', 'PXD', 'LNT', 'DOW', 'CARR', 'MPC', 'ETR', 'HIG', 'VRTX', 'NDAQ',
    'NKE', 'FIS', 'DTE', 'TSN', 'OXY', 'MDLZ', 'PSA', 'CDK', 'MAR', 'FANG'
'GOOGL', 'AAPL', 'MSFT', 'AMZN', 'META', 'TSLA', 'NFLX', 'NVDA', 'INTC', 'CSCO']
selected_ticker = st.selectbox('Select a stock ticker:', tickers)

# Fetch historical stock data
start_date = '2019-01-01'  # Set your start date
end_date = (datetime.now() - timedelta(days=1)).date()  # Set end date to yesterday

# Download the data
data = yf.download(selected_ticker, start=start_date, end=end_date)

# Calculate the 200-day SMA
data['SMA_200'] = data['Close'].rolling(window=200).mean()

# Determine trends and their periods
sma_trend = []
current_trend = None
uptrend_periods = []
downtrend_periods = []

# Identify trends and their start and end dates
for i in range(1, len(data['SMA_200'])):
    if data['SMA_200'].iloc[i] > data['SMA_200'].iloc[i - 1]:
        if current_trend != 'uptrend':
            if current_trend == 'downtrend':
                downtrend_periods[-1][1] = data.index[i - 1]  # Update end date of the last downtrend period
            uptrend_periods.append([data.index[i - 1], None])  # Start new uptrend period
            current_trend = 'uptrend'
    elif data['SMA_200'].iloc[i] < data['SMA_200'].iloc[i - 1]:
        if current_trend != 'downtrend':
            if current_trend == 'uptrend':
                uptrend_periods[-1][1] = data.index[i - 1]  # Update end date of the last uptrend period
            downtrend_periods.append([data.index[i - 1], None])  # Start new downtrend period
            current_trend = 'downtrend'

# Finalize the last period
if current_trend == 'uptrend':
    uptrend_periods[-1][1] = data.index[-1]  # End the last uptrend period
elif current_trend == 'downtrend':
    downtrend_periods[-1][1] = data.index[-1]  # End the last downtrend period

# Filter periods to only include those longer than 50 days
filtered_uptrend_periods = []
for start, end in uptrend_periods:
    if (end - start).days > 50:  # Only keep periods longer than 50 days
        filtered_uptrend_periods.append([start, end])

filtered_downtrend_periods = []
for start, end in downtrend_periods:
    if (end - start).days > 50:  # Only keep periods longer than 50 days
        filtered_downtrend_periods.append([start, end])

# Merge consecutive periods with the same trend, ensuring at least a 50-day gap
merged_uptrend_periods = []
if filtered_uptrend_periods:
    start, end = filtered_uptrend_periods[0]
    for i in range(1, len(filtered_uptrend_periods)):
        next_start, _ = filtered_uptrend_periods[i]
        if next_start <= end + pd.Timedelta(days=50):  # Check if the next start is within 50 days of the current end
            end = filtered_uptrend_periods[i][1]  # Extend the end date
        else:
            merged_uptrend_periods.append([start, end])  # Store the merged period
            start, end = filtered_uptrend_periods[i]  # Start new period
    merged_uptrend_periods.append([start, end])  # Append the last period

# Repeat merging for downtrend periods
merged_downtrend_periods = []
if filtered_downtrend_periods:
    start, end = filtered_downtrend_periods[0]
    for i in range(1, len(filtered_downtrend_periods)):
        next_start, _ = filtered_downtrend_periods[i]
        if next_start <= end + pd.Timedelta(days=50):  # Check if the next start is within 50 days of the current end
            end = filtered_downtrend_periods[i][1]  # Extend the end date
        else:
            merged_downtrend_periods.append([start, end])  # Store the merged period
            start, end = filtered_downtrend_periods[i]  # Start new period
    merged_downtrend_periods.append([start, end])  # Append the last period

# Display results in Streamlit
st.write(f"Number of uptrend periods: {len(merged_uptrend_periods)}")
for start, end in merged_uptrend_periods:
    duration = (end - start).days
    st.write(f"**Uptrend Period:** Start: {start.strftime('%Y-%m-%d')}, End: {end.strftime('%Y-%m-%d')}, Duration: {duration} days")

st.write(f"\nNumber of downtrend periods: {len(merged_downtrend_periods)}")
for start, end in merged_downtrend_periods:
    duration = (end - start).days
    st.write(f"**Downtrend Period:** Start: {start.strftime('%Y-%m-%d')}, End: {end.strftime('%Y-%m-%d')}, Duration: {duration} days")

# Create a Plotly figure
fig = go.Figure()

# Add the closing price trace
fig.add_trace(go.Scatter(
    x=data.index,
    y=data['Close'],
    mode='lines',
    name=f'{selected_ticker} Closing Price',
    line=dict(color='blue')
))

# Color the SMA segments based on trend periods
for start, end in merged_uptrend_periods:
    mask = (data.index >= start) & (data.index <= end)
    fig.add_trace(go.Scatter(
        x=data.index[mask],
        y=data['SMA_200'][mask],
        mode='lines',
        name='200-Day SMA (Uptrend)',
        line=dict(color='green')
    ))

for start, end in merged_downtrend_periods:
    mask = (data.index >= start) & (data.index <= end)
    fig.add_trace(go.Scatter(
        x=data.index[mask],
        y=data['SMA_200'][mask],
        mode='lines',
        name='200-Day SMA (Downtrend)',
        line=dict(color='red')
    ))

# Add gaps between uptrend and downtrend periods in yellow
all_periods = merged_uptrend_periods + merged_downtrend_periods
all_periods.sort(key=lambda x: x[0])  # Sort by start date

for i in range(len(all_periods) - 1):
    current_end = all_periods[i][1]
    next_start = all_periods[i + 1][0]
    if (next_start - current_end).days > 0:  # Check if there's a gap
        fig.add_trace(go.Scatter(
            x=[current_end, next_start],
            y=[data['SMA_200'].loc[current_end], data['SMA_200'].loc[current_end]],  # Get SMA value at current_end
            mode='lines',
            line=dict(color='yellow', width=4),
            name='Gap (Yellow)'
        ))

# Update the layout
fig.update_layout(
    title=f'{selected_ticker} Closing Price and 200-Day SMA',
    xaxis_title='Date',
    yaxis_title='Price (USD)',
    legend=dict(x=-0.1, y=1, traceorder='normal', orientation='v'),  # Adjust legend position
    template='plotly'
)

# Show the figure
st.plotly_chart(fig)
