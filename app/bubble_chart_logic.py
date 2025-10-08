import json
import os
import time
from flask import Blueprint, request
from threading import Thread
from google.protobuf.json_format import MessageToDict

class BubbleChartLogic:
    """
    Manages the business logic for the bubble chart, including handling client
    connections, loading historical data, and broadcasting live ticks.
    """
    def __init__(self, socketio):
        self.socketio = socketio
        self.bp = Blueprint('bubble_chart', __name__, template_folder='../templates')
        self.clients = {}
        self.file_data_cache = {}
        self.available_securities = []

        # Define the history file path relative to the project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.history_file = os.path.join(project_root, "Upstox_date.txt")

        # Start loading the historical data in a background thread.
        self.data_loading_thread = Thread(target=self._load_file_data)
        self.data_loading_thread.daemon = True
        self.data_loading_thread.start()

    def register_handlers(self):
        """Registers all Socket.IO event handlers for the /bubble namespace."""
        namespace = '/bubble'

        @self.socketio.on('connect', namespace=namespace)
        def handle_connect():
            sid = request.sid
            print(f"Client connected: {sid}")
            self.clients[sid] = {'symbol': None}
            # Send the list of available securities once the client connects.
            # This task waits for the initial data load to complete.
            self.socketio.start_background_task(self._send_available_securities, sid)

        @self.socketio.on('request_initial_data', namespace=namespace)
        def handle_data_request(req):
            symbol, sid = req.get('symbol'), request.sid
            if not symbol:
                return
            print(f"Client {sid} requested data for symbol: {symbol}")
            self.clients[sid]['symbol'] = symbol
            self.socketio.join_room(symbol, sid=sid, namespace=namespace)
            # Send historical data for the requested symbol.
            self.socketio.start_background_task(self._send_historical_ticks, symbol, sid)

        @self.socketio.on('disconnect', namespace=namespace)
        def handle_disconnect():
            sid = request.sid
            if sid in self.clients:
                print(f"Client disconnected: {sid}")
                symbol = self.clients[sid].get('symbol')
                if symbol:
                    self.socketio.leave_room(symbol, sid=sid, namespace=namespace)
                del self.clients[sid]

    def _load_file_data(self):
        """
        Loads and caches raw tick data from the history file.
        This runs once on application startup.
        """
        print("Data loading thread started.")
        start_time = time.time()

        if not os.path.exists(self.history_file):
            print(f"History file not found: {self.history_file}")
            return

        print(f"Loading historical data from: {self.history_file}")
        with open(self.history_file, 'r') as f:
            for i, line in enumerate(f):
                try:
                    if not line.strip():
                        continue
                    data = json.loads(line.strip())
                    if 'feeds' in data:
                        for sec_id, feed_data in data['feeds'].items():
                            if 'ltpc' in feed_data:
                                if sec_id not in self.file_data_cache:
                                    self.file_data_cache[sec_id] = []
                                self.file_data_cache[sec_id].append(feed_data['ltpc'])
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON on line {i+1}: {e}")
                except (TypeError, AttributeError) as e:
                    print(f"Error processing data on line {i+1}: {e}")

        self.available_securities = sorted(self.file_data_cache.keys())
        print(f"--> BG_LOAD: File loaded in {time.time() - start_time:.2f}s. Found {len(self.available_securities)} securities.")

    def _send_available_securities(self, sid):
        """
        Waits for data loading and sends the list of available securities to a client.
        """
        print("Preparing to send available securities...")
        self.data_loading_thread.join()  # Wait for the loading thread to complete
        print(f"Sending {len(self.available_securities)} securities to client {sid}.")
        self.socketio.emit('available_securities', {'securities': self.available_securities}, room=sid, namespace='/bubble')

    def _send_historical_ticks(self, security_id, sid):
        """
        Waits for data loading and sends all cached historical ticks for a symbol to a client.
        """
        self.data_loading_thread.join()
        ticks = self.file_data_cache.get(security_id, [])
        print(f"Sending {len(ticks)} historical ticks for {security_id} to {sid}")
        self.socketio.emit('historical_ticks', {'securityId': security_id, 'ticks': ticks}, room=sid, namespace='/bubble')

    def broadcast_live_tick(self, message):
        """
        Processes a live tick from the WebSocket, broadcasts it to relevant clients,
        and updates the list of available securities if a new one is found.
        """
        try:
            message_dict = MessageToDict(message)
            if 'feeds' in message_dict:
                for security_id, data in message_dict['feeds'].items():
                    # If a tick for a new security arrives, add it to the list and notify all clients.
                    if security_id not in self.available_securities:
                        self.available_securities.append(security_id)
                        self.available_securities.sort()
                        print(f"Discovered new security: {security_id}. Broadcasting updated list.")
                        self.socketio.emit('available_securities', {'securities': self.available_securities}, namespace='/bubble')

                    # Broadcast the live tick to clients subscribed to this security's room.
                    if 'ltpc' in data:
                        self.socketio.emit('live_tick', {'securityId': security_id, 'tick': data['ltpc']}, room=security_id, namespace='/bubble')
        except Exception as e:
            print(f"Error broadcasting live tick: {e}")