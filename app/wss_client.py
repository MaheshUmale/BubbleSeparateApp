import os
import json
import pandas as pd
import upstox_client
from google.protobuf.json_format import MessageToDict

class WSSClient:
    """
    Handles the WebSocket connection to Upstox for live market data.
    It manages subscriptions, handles incoming ticks, and saves data to a file.
    """
    def __init__(self, socketio, bubble_chart):
        self.socketio = socketio
        self.bubble_chart = bubble_chart
        self.upstox_streamer = None
        self.subscribed_instrument_keys = set()

        # Define file paths relative to the project root
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.history_file_path = os.path.join(self.project_root, "Upstox_date.txt")

        # Initialize and cache the instrument-to-symbol mapping
        self.instrument_map = self._initialize_instrument_map()

    def _initialize_instrument_map(self):
        """
        Creates and returns a mapping from instrument_key to tradingsymbol.
        Reads from 'instruments.csv' located in the project root.
        """
        instruments_file_path = os.path.join(self.project_root, "instruments.csv")
        print(f"Creating instrument map from: {instruments_file_path}")
        try:
            df = pd.read_csv(instruments_file_path)
            return pd.Series(df.tradingsymbol.values, index=df.instrument_key).to_dict()
        except FileNotFoundError:
            print(f"ERROR: The file {instruments_file_path} was not found.")
            return {}
        except Exception as e:
            print(f"Could not create instrument map: {e}")
            return {}

    def start_websocket_connection(self, access_token):
        """
        Initializes and starts the connection to the Upstox WebSocket API.
        """
        if not access_token:
            self.socketio.emit('backend_status', {'message': 'Upstox Access Token not available.'})
            return
        if self.upstox_streamer and self.upstox_streamer.is_connected():
            print("Streamer is already connected.")
            return

        print("Configuring Upstox API client...")
        config = upstox_client.Configuration()
        config.access_token = access_token
        api_client = upstox_client.ApiClient(config)

        self.upstox_streamer = upstox_client.MarketDataStreamerV3(api_client)

        # Register websocket event handlers
        self.upstox_streamer.on("open", self.on_open)
        self.upstox_streamer.on("message", self.on_message)
        self.upstox_streamer.on("close", self.on_close)
        self.upstox_streamer.on("error", self.on_error)

        try:
            print("Connecting to Upstox WebSocket...")
            self.upstox_streamer.connect()
        except Exception as e:
            print(f"Error connecting to Upstox WebSocket: {e}")
            self.socketio.emit('backend_status', {'message': f'Error connecting to Upstox: {e}.'})

    def on_open(self):
        """Handler for when the WebSocket connection is opened."""
        self.socketio.emit('backend_status', {'message': 'Connected to Upstox market data.'})
        # If there are already subscribed instruments, resubscribe on reconnect
        if self.subscribed_instrument_keys:
            print(f"Resubscribing to {len(self.subscribed_instrument_keys)} instruments on connection open.")
            self.upstox_streamer.subscribe(list(self.subscribed_instrument_keys), "ltpc")

    def on_message(self, message):
        """Handler for incoming messages (ticks) from the WebSocket."""
        self._append_tick_to_file(message)
        self.bubble_chart.broadcast_live_tick(message)

    def on_close(self, code, reason):
        """Handler for when the WebSocket connection is closed."""
        self.socketio.emit('backend_status', {'message': 'Disconnected from Upstox market data.'})
        print(f"Upstox WebSocket connection closed: {code} - {reason}")

    def on_error(self, error):
        """Handler for any WebSocket errors."""
        print(f"Upstox WebSocket error: {error}")
        self.socketio.emit('backend_status', {'message': f'WebSocket Error: {error}'})

    def subscribe(self, instrument_keys: list):
        """Subscribes to a list of new instrument keys."""
        new_keys_to_subscribe = list(set(instrument_keys) - self.subscribed_instrument_keys)

        if not new_keys_to_subscribe:
            print("No new instruments to subscribe.")
            return

        self.subscribed_instrument_keys.update(new_keys_to_subscribe)
        print(f"Requesting subscription for new instruments: {new_keys_to_subscribe}")

        if self.upstox_streamer and self.upstox_streamer.is_connected():
            try:
                self.upstox_streamer.subscribe(new_keys_to_subscribe, "ltpc")
                print(f"Successfully sent subscription request for {len(new_keys_to_subscribe)} instruments.")
            except Exception as e:
                print(f"Failed to subscribe to instruments: {e}. They will be subscribed on (re)connect.")
        else:
            print("Streamer not connected. Keys will be subscribed automatically upon connection.")

    def _append_tick_to_file(self, tick_data):
        """
        Appends a processed tick to the history file.
        """
        try:
            data_to_dump = MessageToDict(tick_data)

            # Add the 'ticker' symbol to each feed for easier identification
            if 'feeds' in data_to_dump:
                for key, feed_data in data_to_dump['feeds'].items():
                    feed_data['ticker'] = self.instrument_map.get(key, 'UNKNOWN')

            with open(self.history_file_path, 'a') as f:
                json.dump(data_to_dump, f)
                f.write('\n')
        except Exception as e:
            print(f"Error writing tick to file: {e}")