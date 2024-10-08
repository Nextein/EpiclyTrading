import logging
import os
import pandas as pd
import requests
import mplfinance as mpf  # For candlestick plotting
from indicators import squeeze  # Assuming this function exists in indicators.py
import matplotlib.pyplot as plt

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

logging.info("Script started")

# Fetch historical data for each ticker based on timeframe
def fetch_data(ticker, interval):
    url = f"https://api.binance.com/api/v1/klines?symbol={ticker}&interval={interval}"
    logging.info(f"Fetching {interval} data for {ticker}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # Select only the first 6 columns (Time, Open, High, Low, Close, Volume)
        df = pd.DataFrame(data, columns=[
            'Time', 'Open', 'High', 'Low', 'Close', 'Volume', '_', '_', '_', '_', '_', '_'
        ])
        df = df[['Time', 'Open', 'High', 'Low', 'Close', 'Volume']]
        df['Time'] = pd.to_datetime(df['Time'], unit='ms')
        df.set_index('Time', inplace=True)
        df = df.astype(float)  # Ensure all columns are float
        df = df.tail(100)
        logging.info(f"Fetched {interval} data for {ticker}.")
        return df
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {interval} data for {ticker}: {e}")
        return None

# Plot OHLCV candles and squeeze indicator for each ticker
def plot_price_and_squeeze(ticker, data):
    logging.info(f"Plotting OHLCV candles and squeeze indicator for {ticker}...")

    squeeze_values = squeeze(data)

    # Plotting using mplfinance for candlestick chart
    fig, axes = mpf.plot(
        data,
        type='candle',  # Plot candlesticks
        volume=True,  # Show volume subplot
        mav=(20, 50),  # Moving averages (optional)
        title=f"{ticker} - OHLCV Candlestick Chart",
        ylabel="Price",
        ylabel_lower="Volume",
        returnfig=True,
        style="yahoo",  # Use the 'yahoo' style for the chart
    )

    # Add squeeze indicator on a secondary axis (below the candlestick chart)
    ax_squeeze = fig.add_axes([0.125, 0.05, 0.775, 0.15])  # Position the squeeze indicator below the chart
    ax_squeeze.plot(data.index, squeeze_values, label='Squeeze Indicator', color='r')
    ax_squeeze.set_title('Squeeze Indicator')
    ax_squeeze.set_ylabel('Squeeze')
    ax_squeeze.grid(True)
    ax_squeeze.legend()

    plt.show(block=False)  # Non-blocking show
    plt.pause(5)  # Show for 10 seconds
    plt.close()  # Close the plot after 10 seconds

# Read the watchlist file and fetch historical data for each ticker
def read_watchlist_and_plot(watchlist_file, interval='1d'):
    if not os.path.exists(watchlist_file):
        logging.error(f"Watchlist file {watchlist_file} not found.")
        return
    
    with open(watchlist_file, 'r') as f:
        tickers = [line.strip() for line in f.readlines()]

    for ticker in tickers:
        logging.info(f"Processing {ticker}...")
        data = fetch_data(ticker, interval)
        if data is not None and not data.empty:
            plot_price_and_squeeze(ticker, data)
        else:
            logging.warning(f"No valid data for {ticker}.")

import glob  # For file pattern matching

# Main execution
if __name__ == "__main__":
    # Specify the watchlist file
    file = input("Enter the watchlist file name (leave blank for last created): ")

    # Default timeframe if no file is specified
    if file.strip() == "":
        # Get all watchlist files that match the naming structure
        files = glob.glob('watchlists/watchlist_*.txt')

        if files:  # If there are any matching files
            # Sort files by modification time and select the latest
            latest_file = max(files, key=os.path.getmtime)
            print(f"Using the last created watchlist file: {latest_file}")
            watchlist_file = latest_file
        else:
            print("No watchlist files found in the directory.")
            watchlist_file = None  # Set to None or handle accordingly
    else:
        watchlist_file = f'watchlists/{file}.txt'
    
    # If a valid watchlist file was found, proceed
    if watchlist_file:
        interval = input("Enter the timeframe (e.g., '1d', '1h', '15m', default '1d'): ")
        if not interval.strip():  # If still empty, set a default timeframe
            interval = '1d'
        read_watchlist_and_plot(watchlist_file, interval)
    else:
        logging.error("No valid watchlist file available.")

logging.info("Script finished.")

