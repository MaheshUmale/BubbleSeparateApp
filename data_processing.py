import pandas as pd
import time
import glob
import os

def get_instrument_keys_from_bbscan(bbscan_pattern="BBSCAN_FIRED_*.csv", instruments_file="instruments.csv"):
    """
    Reads tickers from the latest BBSCAN file and maps them to instrument keys.
    """
    try:
        # Find the latest BBSCAN file based on the pattern
        list_of_files = glob.glob(bbscan_pattern)
        if not list_of_files:
            print(f"No files found with pattern: {bbscan_pattern}")
            return []

        latest_file = max(list_of_files, key=os.path.getctime)
        print(f"Processing file: {latest_file}")

        # Read the tickers from the BBSCAN file
        bbscan_df = pd.read_csv(latest_file)
        tickers = bbscan_df['ticker'].unique().tolist()

        # Read the instruments mapping file
        instruments_df = pd.read_csv(instruments_file)

        # Filter the instruments to get the keys for the required tickers
        # The 'tradingsymbol' in instruments.csv corresponds to 'ticker' in the BBSCAN file
        instrument_keys = instruments_df[instruments_df['tradingsymbol'].isin(tickers)]['instrument_key'].tolist()

        return instrument_keys

    except FileNotFoundError:
        print(f"Error: The file {instruments_file} or a BBSCAN file was not found.")
        return []
    except Exception as e:
        print(f"An error occurred in get_instrument_keys_from_bbscan: {e}")
        return []

def start_symbol_subscription_thread(wss_client):
    """
    A background thread that periodically checks for new symbols in the BBSCAN file
    and subscribes to them via the WebSocket client.
    """
    subscribed_keys = set()

    while True:
        print("Checking for new symbols to subscribe...")

        # Wait for the WebSocket connection to be established
        if not wss_client.upstox_streamer:
            print("WebSocket client not connected. Waiting...")
            time.sleep(10)
            continue

        instrument_keys = get_instrument_keys_from_bbscan()

        new_keys_to_subscribe = [key for key in instrument_keys if key not in subscribed_keys]

        if new_keys_to_subscribe:
            print(f"Found new symbols to subscribe: {new_keys_to_subscribe}")
            wss_client.subscribe(new_keys_to_subscribe)
            subscribed_keys.update(new_keys_to_subscribe)
        else:
            print("No new symbols found.")

        # Wait for 2 minutes before checking again
        time.sleep(120)