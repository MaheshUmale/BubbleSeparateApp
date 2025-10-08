import json
import os
import traceback
import time
from flask import Blueprint, render_template, request
from flask_socketio import emit
from threading import Thread
from datetime import datetime

class BubbleChartLogic:
    def __init__(self, socketio):
        self.socketio = socketio
        self.bp = Blueprint('bubble_chart', __name__, template_folder='templates')
        self.clients = {}
        self.file_data_cache = {}
        self.available_securities = []
        self.HISTORY_FILE = "Upstox_date.txt"

        # Start loading the file in a background thread.
        self.data_loading_thread = Thread(target=self._load_file_data)
        self.data_loading_thread.daemon = True
        self.data_loading_thread.start()

    def register_handlers(self):
        namespace = '/bubble'

        @self.socketio.on('connect', namespace=namespace)
        def handle_connect():
            sid = request.sid
            print(f"Client connected: {sid}")
            self.clients[sid] = {'symbol': None}
            # This task will wait for file loading and then send the securities list.
            self.socketio.start_background_task(self._send_available_securities, sid)

        @self.socketio.on('request_initial_data', namespace=namespace)
        def handle_data_request(req):
            symbol, sid = req.get('symbol'), request.sid
            if not symbol: return
            print(f"Client {sid} requested data for symbol: {symbol}")
            self.clients[sid]['symbol'] = symbol
            self.socketio.join_room(symbol, sid=sid, namespace=namespace)
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
        """Loads raw tick data from the history file into the cache."""
        print("Data loading thread started.")
        start_time = time.time()

        if not os.path.exists(self.HISTORY_FILE):
            print(f"History file not found: {self.HISTORY_FILE}")
            return

        print(f"Loading historical data from: {self.HISTORY_FILE}")
        with open(self.HISTORY_FILE, 'r') as f:
            for i, line in enumerate(f):
                try:
                    if not line.strip(): continue
                    data = json.loads(line.strip())
                    if data.get('feeds'):
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
        """Waits for data loading and sends the list of available securities to a client."""
        print("Preparing to send available securities...")
        self.data_loading_thread.join()  # Wait for the loading thread to complete
        print(f"Sending {len(self.available_securities)} securities to client {sid}.")
        self.socketio.emit('available_securities', {'securities': self.available_securities}, room=sid, namespace='/bubble')

    def _send_historical_ticks(self, security_id, sid):
        """Waits for data loading and sends all historical ticks for a symbol."""
        self.data_loading_thread.join()
        ticks = self.file_data_cache.get(security_id, [])
        print(f"Sending {len(ticks)} historical ticks for {security_id} to {sid}")
        self.socketio.emit('historical_ticks', {'securityId': security_id, 'ticks': ticks}, room=sid, namespace='/bubble')

    def broadcast_live_tick(self, message):
        """Broadcasts a raw live tick to clients."""
        if hasattr(message, 'feeds') and isinstance(message.feeds, dict):
            for security_id, data in message.feeds.items():
                if security_id in self.available_securities:
                    feed = data.to_dict()
                    if 'ltpc' in feed:
                        self.socketio.emit('live_tick', {'securityId': security_id, 'tick': feed['ltpc']}, room=security_id, namespace='/bubble')