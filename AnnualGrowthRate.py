import streamlit as st
import yfinance as yf
import pandas as pd

# Function to inject CSS for equal table column widths
def add_table_style():
    st.markdown(
        """
        <style>
        .dataframe tbody tr th, .dataframe thead tr th {
            text-align: center;
            width: 50%;
        }
        .dataframe td {
            text-align: center;
            width: 50%;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Streamlit app title
st.title('Stock Annual Growth Rate Calculator')

# Inject the custom CSS for the table
add_table_style()

# User input for stock ticker
ticker = st.text_input('Enter Stock Ticker Symbol:', 'AAPL')

# User input for number of years
num_years = st.slider('Select Number of Years:', min_value=1, max_value=20, value=10)

# Fetch historical data
if ticker:
    try:
        # Calculate start date based on number of years
        end_date = pd.Timestamp.today().strftime('%Y-%m-%d')
        start_date = (pd.Timestamp.today() - pd.DateOffset(years=num_years)).strftime('%Y-%m-%d')
        
        # Fetch data
        data = yf.download(ticker, start=start_date, end=end_date, interval='1mo')

        # Resample to annual data
        annual_data = data['Adj Close'].resample('Y').last()

        # Calculate annual growth rate
        annual_growth_rate = annual_data.pct_change() * 100

        # Calculate average annual growth rate
        average_growth_rate = annual_growth_rate.mean()

        # Display results in a styled table
        st.subheader(f'Annual Growth Rates for {ticker}')
        st.dataframe(pd.DataFrame(annual_growth_rate).rename(columns={'Adj Close': 'Annual Growth Rate (%)'}))
        st.write(f'Average Annual Growth Rate: {average_growth_rate:.2f}%')
        
    except Exception as e:
        st.error(f"Error fetching data for ticker {ticker}: {e}")
