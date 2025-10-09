import pandas as pd
import time
import glob
import os

def get_instrument_keys_from_bbscan(project_root):
    """
    Reads tickers from the latest BBSCAN file in the project root and maps them
    to instrument keys using the 'instruments.csv' file.

    Args:
        project_root (str): The absolute path to the project's root directory.

    Returns:
        list: A list of instrument keys corresponding to the tickers in the BBSCAN file.
    """
    try:
        bbscan_pattern = os.path.join(project_root, "BBSCAN_FIRED_*.csv")
        instruments_file = os.path.join(project_root, "instruments.csv")

        # Find the latest BBSCAN file based on the pattern
        list_of_files = glob.glob(bbscan_pattern)
        if not list_of_files:
            print(f"No BBSCAN files found with pattern: {bbscan_pattern}")
            return []

        latest_file = max(list_of_files, key=os.path.getctime)
        print(f"Processing BBSCAN file: {latest_file}")

        # Read tickers from the BBSCAN file
        bbscan_df = pd.read_csv(latest_file)
        tickers = bbscan_df['ticker'].unique().tolist()

        # Read the instruments mapping file
        instruments_df = pd.read_csv(instruments_file)

        # Filter instruments to get keys for the required tickers
        instrument_keys = instruments_df[instruments_df['tradingsymbol'].isin(tickers)]['instrument_key'].tolist()

        print(f"Found {len(instrument_keys)} instrument keys for {len(tickers)} unique tickers.")
        return instrument_keys

    except FileNotFoundError as e:
        print(f"Error: A required file was not found. {e}")
        return []
    except Exception as e:
        print(f"An error occurred in get_instrument_keys_from_bbscan: {e}")
        return []

def start_symbol_subscription_thread(wss_client):
    """
    A background thread that periodically checks for new symbols in the BBSCAN file
    and subscribes to them via the WebSocket client.

    Args:
        wss_client (WSSClient): An instance of the WebSocket client.
    """
    subscribed_keys = set()
    project_root = wss_client.project_root # Get project root from the WSS client

    while True:
        print("Checking for new symbols to subscribe...")

        # Wait for the WebSocket connection to be fully established
        if not wss_client.is_connected():
            print("WebSocket client not connected. Waiting for connection...")
            time.sleep(10) 
            continue

        instrument_keys = get_instrument_keys_from_bbscan(project_root)

        # Determine which keys are new and need to be subscribed
        new_keys_to_subscribe = [key for key in instrument_keys if key not in subscribed_keys]

        if new_keys_to_subscribe:
            print(f"Found {len(new_keys_to_subscribe)} new symbols to subscribe.")
            wss_client.subscribe(new_keys_to_subscribe)
            subscribed_keys.update(new_keys_to_subscribe)
        else:
            print("No new symbols found to subscribe.")

        # Wait for 2 minutes before the next check
        print("Waiting for 2 minutes before next symbol check...")
        time.sleep(120)