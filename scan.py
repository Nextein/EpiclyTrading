# Import required libraries and your indicators
import logging
import requests
import pandas as pd
from datetime import datetime
import os  # Import os module to handle directory operations
from indicators import relativeCandlesReversalPatterns, Cycles, relativeCandlesPhases

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

logging.info("Script started")

# Fetch list of futures tickers from Binance API
def fetch_futures_tickers():
    url = "https://api.binance.com/api/v1/exchangeInfo"
    logging.info("Fetching list of futures tickers from Binance API...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        tickers = [item['symbol'] for item in data['symbols'] if item['quoteAsset'] == 'USDT']
        logging.info(f"Fetched {len(tickers)} futures tickers.")
        return tickers
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching futures tickers: {e}")
        return []

# Fetch historical data for each ticker based on timeframe
def fetch_data(ticker, interval):
    url = f"https://api.binance.com/api/v1/klines?symbol={ticker}&interval={interval}"
    logging.info(f"Fetching {interval} data for {ticker}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume', '_', '_', '_', '_', '_', '_'])
        df['Time'] = pd.to_datetime(df['Time'], unit='ms')
        df.set_index('Time', inplace=True)
        logging.info(f"Fetched {interval} data for {ticker}.")
        return df
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {interval} data for {ticker}: {e}")
        return None

# Apply technical analysis to each ticker
def apply_technical_analysis(data):
    logging.info("Applying technical analysis...")
    reversal_pattern = relativeCandlesReversalPatterns(data)
    cycles = Cycles(data)
    phases = relativeCandlesPhases(data)
    logging.info(f"Reversal Pattern: {reversal_pattern}")
    logging.info(f"Cycles: {cycles.iloc[-1]}")
    logging.info(f"Phases: {phases[-1]}")
    return reversal_pattern, cycles, phases

# Add tickers to watchlist if they meet certain criteria
def evaluate_ticker(ticker, data):
    logging.info(f"Evaluating {ticker} for potential watchlist addition...")
    reversal_pattern, cycles, phases = apply_technical_analysis(data)
    
    # Define criteria to add to the watchlist
    if reversal_pattern == 1:  # Buy sequence
        logging.info(f"{ticker} meets buy sequence criteria. Adding to watchlist.")
        return True
    elif reversal_pattern == -1:  # Sell sequence
        logging.info(f"{ticker} meets sell sequence criteria. Adding to watchlist.")
        return True
    else:
        logging.info(f"{ticker} does not meet any criteria. Skipping.")
        return False

# Main script execution
def main():
    watchlists = {}
    tickers = fetch_futures_tickers()
    
    # Define the timeframes to analyze
    timeframes = ['1h', '4h', '1d', '1w','15m', '30m']
    
    # Create watchlists directory if it doesn't exist
    watchlists_dir = 'watchlists'
    os.makedirs(watchlists_dir, exist_ok=True)

    for timeframe in timeframes:
        watchlist = []
        logging.info(f"Analyzing tickers for {timeframe} timeframe...")
        
        for ticker in tickers:
            data = fetch_data(ticker, timeframe)
            if data is not None:
                if evaluate_ticker(ticker, data):
                    watchlist.append(ticker)
        
        # Generate filename with date, hour, and timeframe
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M")
        filename = os.path.join(watchlists_dir, f'watchlist_{timeframe}_{timestamp}.txt')
        
        # Output watchlist to file
        with open(filename, 'w') as f:
            logging.info(f"Writing watchlist for {timeframe} to file: {filename}...")
            for ticker in watchlist:
                f.write(f"{ticker}\n")
        
        logging.info(f"Watchlist for {timeframe} saved with {len(watchlist)} tickers.")

if __name__ == "__main__":
    main()

logging.info("Script finished.")
