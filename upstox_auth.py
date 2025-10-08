import os
import requests
import configparser
from flask import Blueprint, redirect, request, session, url_for, render_template, flash
from threading import Thread

# This will hold the function to start the websocket connection, passed from app.py
start_websocket_connection = None

# --- Blueprint Setup ---
upstox_auth_bp = Blueprint('upstox_auth', __name__, template_folder='templates')

def load_properties_file():
    """Loads properties from my.properties file using an absolute path."""
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = os.path.join(APP_ROOT, 'my.properties')

    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"'{CONFIG_PATH}' file not found.")
    config.read(CONFIG_PATH)

    return (
        config['DEFAULT']['apikey'],
        config['DEFAULT']['secret'],
        "http://127.0.0.1:8080/upstox/callback"
    )

def get_access_token(code, client_id, client_secret, redirect_uri):
    """Exchanges authorization code for access token."""
    url = "https://api.upstox.com/v2/login/authorization/token"
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json().get('access_token')
    except requests.exceptions.RequestException as e:
        print(f"Error getting access token: {e}")
        return None

def initialize_auth(app):
    """Initializes the authentication module with app context."""
    global start_websocket_connection
    start_websocket_connection = app.start_upstox_websocket_connection

@upstox_auth_bp.route('/login')
def login_page():
    """Renders the page with the Upstox login button."""
    return render_template('upstox_login.html')

@upstox_auth_bp.route("/authorize")
def authorize():
    """Redirects the user to Upstox to authorize the application."""
    client_id, _, redirect_uri = load_properties_file()
    auth_url = f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
    return redirect(auth_url)

@upstox_auth_bp.route('/callback')
def callback():
    """Handles the callback from Upstox after authorization."""
    code = request.args.get('code')
    if not code:
        flash('Authorization failed: No code provided.', 'error')
        return redirect(url_for('upstox_auth.login_page'))

    client_id, client_secret, redirect_uri = load_properties_file()
    token = get_access_token(code, client_id, client_secret, redirect_uri)

    if token:
        session['upstox_access_token'] = token
        flash('Successfully logged in to Upstox!', 'success')

        if start_websocket_connection:
            websocket_thread = Thread(target=start_websocket_connection, args=(token,), daemon=True)
            websocket_thread.start()

        return redirect(url_for('index'))
    else:
        flash('Failed to get access token from Upstox.', 'error')
        return redirect(url_for('upstox_auth.login_page'))