import os
import sys
import threading
from flask import Flask, session, render_template, redirect, url_for, send_from_directory
from flask_socketio import SocketIO

def create_app():
    """
    Create and configure the Flask application and its extensions.
    This function acts as the application factory.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',  # Replace with a real secret key in production
    )

    # --- Configuration ---
    # Define paths relative to the application's root directory
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = os.path.join(APP_ROOT, '..', 'my.properties') # Config is in the parent directory

    # Ensure the config file exists before proceeding
    if not os.path.exists(CONFIG_PATH):
        print(f"FATAL ERROR: Configuration file not found at `{CONFIG_PATH}`.", file=sys.stderr)
        print("Please create `my.properties` with your Upstox API key and secret.", file=sys.stderr)
        sys.exit(1)

    # --- Extensions ---
    socketio = SocketIO(app, cors_allowed_origins="*")

    # --- Application Components ---
    from . import upstox_auth, wss_client, data_processing, bubble_chart_logic

    # Initialize logic and blueprints
    bubble_chart = bubble_chart_logic.BubbleChartLogic(socketio)
    bubble_chart.register_handlers()
    app.register_blueprint(bubble_chart.bp)
    app.register_blueprint(upstox_auth.upstox_auth_bp, url_prefix='/upstox')

    # --- WebSocket and Background Task Setup ---
    # Initialize the WebSocket client
    websocket_client = wss_client.WSSClient(socketio, bubble_chart)

    # Pass the websocket connection starter to the auth module
    # This allows the auth blueprint to trigger the websocket connection upon successful login
    upstox_auth.set_websocket_starter(websocket_client.start_websocket_connection)
    # This function is now a pass-through, but we call it for consistency.
    upstox_auth.initialize_auth(app)

    # Start the background thread for processing the BBSCAN file and subscribing to symbols
    subscription_thread = threading.Thread(
        target=data_processing.start_symbol_subscription_thread,
        args=(websocket_client,),
        daemon=True
    )
    subscription_thread.start()

    # --- Main Routes ---
    @app.route('/')
    def index():
        """
        Renders the main bubble chart page if the user is logged in;
        otherwise, redirects to the login page.
        """
        if 'upstox_access_token' in session:
            return render_template('BubbleChart.html')
        else:
            return redirect(url_for('upstox_auth.login_page'))

    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """Serves static files from the root 'static' directory."""
        return send_from_directory(os.path.join(app.root_path, '..', 'static'), filename)

    return app, socketio