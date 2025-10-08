import os
import requests
import configparser
from flask import Blueprint, redirect, request, session, url_for, render_template, flash
from threading import Thread

# --- Globals ---
# This will hold the function to start the websocket connection.
# It's injected from the main app factory to avoid circular imports.
_start_websocket_connection = None

# --- Blueprint Setup ---
# The template folder is now relative to the app's root.
upstox_auth_bp = Blueprint('upstox_auth', __name__, template_folder='../templates')

# --- Helper Functions ---

def set_websocket_starter(starter_func):
    """
    Dependency injector for the websocket starter function.
    This is called from the app factory.
    """
    global _start_websocket_connection
    _start_websocket_connection = starter_func

def load_properties_file():
    """
    Loads properties from the my.properties file located in the project root.
    """
    # The config file is in the parent directory of this blueprint's root path.
    config_path = os.path.join(os.path.dirname(__file__), '..', 'my.properties')

    config = configparser.ConfigParser()
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file '{config_path}' not found.")

    config.read(config_path)

    # The callback URL should be defined here, pointing to this blueprint's endpoint.
    redirect_uri = "http://127.0.0.1:8080/upstox/callback"

    return (
        config['DEFAULT']['apikey'],
        config['DEFAULT']['secret'],
        redirect_uri
    )

def get_access_token(code, client_id, client_secret, redirect_uri):
    """
    Exchanges the authorization code for an access token from the Upstox API.
    """
    url = "https://api.upstox.com/v2/login/authorization/token"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json().get('access_token')
    except requests.exceptions.RequestException as e:
        print(f"Error getting access token: {e}")
        flash(f"Error communicating with Upstox: {e}", "error")
        return None

# --- Routes ---

@upstox_auth_bp.route('/login')
def login_page():
    """
    Renders the page with the Upstox login button.
    """
    return render_template('upstox_login.html')

@upstox_auth_bp.route("/authorize")
def authorize():
    """
    Redirects the user to the Upstox authorization page.
    """
    try:
        client_id, _, redirect_uri = load_properties_file()
        auth_url = f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
        return redirect(auth_url)
    except FileNotFoundError as e:
        flash(str(e), "error")
        return redirect(url_for('upstox_auth.login_page'))

@upstox_auth_bp.route('/callback')
def callback():
    """
    Handles the callback from Upstox after the user has authorized the app.
    It receives the auth code, exchanges it for an access token, and starts the websocket.
    """
    code = request.args.get('code')
    if not code:
        flash('Authorization failed: No authorization code was provided by Upstox.', 'error')
        return redirect(url_for('upstox_auth.login_page'))

    try:
        client_id, client_secret, redirect_uri = load_properties_file()
        token = get_access_token(code, client_id, client_secret, redirect_uri)

        if token:
            session['upstox_access_token'] = token
            flash('Successfully logged in to Upstox!', 'success')

            if _start_websocket_connection:
                # Start the websocket connection in a background thread
                websocket_thread = Thread(target=_start_websocket_connection, args=(token,), daemon=True)
                websocket_thread.start()
            else:
                flash("Websocket connection could not be started.", "error")

            return redirect(url_for('index'))
        else:
            flash('Failed to get access token from Upstox. Please try again.', 'error')
            return redirect(url_for('upstox_auth.login_page'))

    except FileNotFoundError as e:
        flash(str(e), "error")
        return redirect(url_for('upstox_auth.login_page'))
    except Exception as e:
        flash(f"An unexpected error occurred: {e}", "error")
        return redirect(url_for('upstox_auth.login_page'))

# This function is no longer needed as the app factory will handle initialization
def initialize_auth(app):
    pass