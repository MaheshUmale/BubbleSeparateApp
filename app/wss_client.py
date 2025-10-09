import os
import json
import pandas as pd
import upstox_client
from google.protobuf.json_format import MessageToDict
import threading
from flask_socketio import SocketIO, join_room, leave_room
import configparser

import websocket
import rel
import time
import json
import upstox_client
from datetime import datetime

UpstoxWSS_JSONFilename = 'UpstoxWSS_' + datetime.now().strftime('%d_%m_%y') + '.txt'
FILEPATH = 'static/'+UpstoxWSS_JSONFilename

# Connection states
DISCONNECTED = "DISCONNECTED"
CONNECTING = "CONNECTING"
CONNECTED = "CONNECTED"

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
        self.connection_state = DISCONNECTED
        self.connection_lock = threading.Lock()
        self.access_token = None

        # Define file paths relative to the project root
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.history_file_path = os.path.join(self.project_root, FILEPATH)

        # Initialize and cache the instrument-to-symbol mapping
        self.instrument_map = self._initialize_instrument_map()
        self.symbol_to_key_map = {value: key for key, value in self.instrument_map.items()}

    def _initialize_instrument_map(self):
        """
        Creates and returns a mapping from instrument_key to tradingsymbol.
        Reads from 'instruments.csv' located in the project root.
        """
        instruments_file_path = os.path.join(self.project_root, "instruments.csv")
        # Create the inverse map

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
        This is the single entry point for managing the connection lifecycle.
        """
        with self.connection_lock:
            if self.connection_state in [CONNECTED, CONNECTING]:
                print(f"WebSocket connection attempt ignored. State: {self.connection_state}")
                return

            self.connection_state = CONNECTING
            self.access_token = access_token

        if not self.access_token:
            self.socketio.emit('backend_status', {'message': 'Upstox Access Token not available.'})
            self.connection_state = DISCONNECTED
            return

        print("Configuring Upstox API client...")
        config = upstox_client.Configuration()
        config.access_token = self.access_token
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
            self.connection_state = DISCONNECTED

    def disconnect(self):
        """
        Disconnects the WebSocket client and resets the state.
        """
        with self.connection_lock:
            if self.upstox_streamer and self.connection_state != DISCONNECTED:
                print("Disconnecting from Upstox WebSocket...")
                self.upstox_streamer.disconnect()
            self.connection_state = DISCONNECTED
            self.upstox_streamer = None

    def on_open(self):
        """Handler for when the WebSocket connection is opened."""
        with self.connection_lock:
            self.connection_state = CONNECTED
        self.socketio.emit('backend_status', {'message': 'Connected to Upstox market data.'})
        if self.subscribed_instrument_keys:
            print(f"Resubscribing to {len(self.subscribed_instrument_keys)} instruments on connection open.")
            self.upstox_streamer.subscribe(list(self.subscribed_instrument_keys), "ltpc")

    def on_message(self, message):
        """Handler for incoming messages (ticks) from the WebSocket."""
        messageWithTickerNAme = self._append_tick_to_file(message)
        if(messageWithTickerNAme):
            self.bubble_chart.broadcast_live_tick(messageWithTickerNAme)

    def on_close(self, code, reason):
        """Handler for when the WebSocket connection is closed."""
        self.socketio.emit('backend_status', {'message': 'Disconnected from Upstox market data.'})
        print(f"Upstox WebSocket connection closed: {code} - {reason}")
        self.disconnect()
        self.reconnect()

    def on_error(self, error):
        """Handler for any WebSocket errors."""
        print(f"Upstox WebSocket error: {error}")
        self.socketio.emit('backend_status', {'message': f'WebSocket Error: {error}'})
        self.disconnect()
        self.reconnect()

    def reconnect(self):
        """
        Initiates a reconnection attempt after a delay.
        """
        with self.connection_lock:
            if self.connection_state == DISCONNECTED:
                print("Attempting to reconnect...")
                time.sleep(5)  # Wait for 5 seconds before reconnecting
                self.start_websocket_connection(self.access_token)

    def subscribe(self, instrument_keys: list):
        """Subscribes to a list of new instrument keys."""
        
        # Use the key itself as the default value GETTING INVERSE OF SYMBOLS INTO KEYS FOR UPSTOX TO UNDERSTAND 
        symbols_list = [self.symbol_to_key_map.get(key, key) for key in instrument_keys]
        instrument_keys=symbols_list
        print(" instrument_keys ===> "+instrument_keys)

        new_keys_to_subscribe = list(set(instrument_keys) - self.subscribed_instrument_keys)

        if not new_keys_to_subscribe:
            print("No new instruments to subscribe.")
            return

        self.subscribed_instrument_keys.update(new_keys_to_subscribe)
        print(f"Requesting subscription for new instruments: {new_keys_to_subscribe}")

        if self.upstox_streamer and self.is_connected():
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
            
                return json.dumps(data_to_dump)
            
        except Exception as e:
            print(f"Error writing tick to file: {e}")

    def is_connected(self):
        """Returns the custom connection status flag."""
        return self.connection_state == CONNECTED
    
