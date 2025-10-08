import json
from datetime import datetime
import upstox_client
from google.protobuf.json_format import MessageToDict
import pandas as pd

# --- Instrument Mapping Cache ---
instrument_map_cache = None

def get_instrument_map():
    """Creates and caches a mapping from instrument_key to tradingsymbol."""
    global instrument_map_cache
    if instrument_map_cache is None:
        print("Creating instrument map from instruments.csv...")
        try:
            df = pd.read_csv("instruments.csv")
            instrument_map_cache = pd.Series(df.tradingsymbol.values, index=df.instrument_key).to_dict()
            print("Instrument map created successfully.")
        except Exception as e:
            print(f"Could not create instrument map: {e}")
            instrument_map_cache = {}
    return instrument_map_cache

class WSSClient:
    def __init__(self, socketio, bubble_chart):
        self.socketio = socketio
        self.bubble_chart = bubble_chart
        self.upstox_streamer = None
        self.subscribed_instrument_keys = set()
        get_instrument_map()  # Pre-cache the map on initialization

    def start_websocket_connection(self, access_token):
        if not access_token:
            self.socketio.emit('backend_status', {'message': 'Upstox Access Token not available.'})
            return
        if self.upstox_streamer:
            print("Streamer already running.")
            return

        config = upstox_client.Configuration()
        config.access_token = access_token
        api_client = upstox_client.ApiClient(config)
        self.upstox_streamer = upstox_client.MarketDataStreamerV3(api_client)

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
        self.socketio.emit('backend_status', {'message': 'Connected to Upstox market data.'})
        if self.subscribed_instrument_keys:
            print(f"Resubscribing to {len(self.subscribed_instrument_keys)} instruments on connection open.")
            self.upstox_streamer.subscribe(list(self.subscribed_instrument_keys), "ltpc")

    def on_message(self, message):
        self.append_tick_to_file(message)
        self.bubble_chart.broadcast_live_tick(message)

    def on_close(self):
        self.socketio.emit('backend_status', {'message': 'Disconnected from Upstox market data.'})
        print("Upstox WebSocket connection closed.")

    def on_error(self, error):
        print(f"Upstox WebSocket error: {error}")
        self.socketio.emit('backend_status', {'message': f'WebSocket Error: {error}'})

    def subscribe(self, instrument_keys: list):
        """Subscribes to a list of instrument keys."""
        new_keys_to_subscribe = list(set(instrument_keys) - self.subscribed_instrument_keys)

        if not new_keys_to_subscribe:
            return

        self.subscribed_instrument_keys.update(new_keys_to_subscribe)
        print(f"New instruments to subscribe: {new_keys_to_subscribe}")

        if self.upstox_streamer:
            try:
                self.upstox_streamer.subscribe(new_keys_to_subscribe, "ltpc")
                print(f"Successfully sent subscription request for {new_keys_to_subscribe}")
            except Exception as e:
                print(f"Failed to subscribe to {new_keys_to_subscribe}: {e}. They will be subscribed on (re)connect.")
        else:
            print("Streamer not initialized. Keys will be subscribed on connect.")

    def append_tick_to_file(self, tick_data):
        filepath = "Upstox_date.txt"

        data_to_dump = MessageToDict(tick_data)

        if 'feeds' in data_to_dump:
            for key in list(data_to_dump['feeds']):
                ticker = get_instrument_map().get(key, 'UNKNOWN')
                data_to_dump['feeds'][key]['ticker'] = ticker

        with open(filepath, 'a') as f:
            json.dump(data_to_dump, f)
            f.write('\n')