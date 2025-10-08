import os
import sys
import threading
from flask import Flask, render_template, send_from_directory, session, redirect, url_for
from flask_socketio import SocketIO

# Import custom modules
from bubble_chart_logic import BubbleChartLogic
from upstox_auth import upstox_auth_bp, initialize_auth
from wss_client import WSSClient
from data_processing import start_symbol_subscription_thread

# --- Main Application Execution ---
if __name__ == '__main__':
    # Define the absolute path for the config file
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = os.path.join(APP_ROOT, 'my.properties')

    # Check for config file before starting
    if not os.path.exists(CONFIG_PATH):
        print(f"FATAL ERROR: `{CONFIG_PATH}` not found.", file=sys.stderr)
        print("Please create it with your Upstox API key and secret.", file=sys.stderr)
        sys.exit(1)

    # Flask and Socket.IO Setup
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_for_flask_session'
    socketio = SocketIO(app, cors_allowed_origins="*")

    # Initialize Logic and Blueprints
    bubble_chart = BubbleChartLogic(socketio)
    bubble_chart.register_handlers()
    app.register_blueprint(bubble_chart.bp)
    app.register_blueprint(upstox_auth_bp, url_prefix='/upstox')

    # --- Flask Routes ---
    @app.route('/')
    def index():
        """
        Renders the main bubble chart page if logged in,
        otherwise redirects to the login page.
        """
        if 'upstox_access_token' in session:
            return render_template('BubbleChart.html')
        else:
            return redirect(url_for('upstox_auth.login_page'))

    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """Serves static files."""
        return send_from_directory('static', filename)

    try:
        if not os.path.exists('static'):
            os.makedirs('static')

        # Initialize the WebSocket client
        wss_client = WSSClient(socketio, bubble_chart)

        # Pass the websocket connection starter to the auth module
        app.start_upstox_websocket_connection = wss_client.start_websocket_connection
        initialize_auth(app)

        # Start the thread for processing the BBSCAN file and subscribing to symbols
        subscription_thread = threading.Thread(target=start_symbol_subscription_thread, args=(wss_client,), daemon=True)
        subscription_thread.start()

        print("Starting Flask server with Socket.IO on port 8080...")
        socketio.run(app, debug=True, use_reloader=False, allow_unsafe_werkzeug=True, port=8080)

    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()