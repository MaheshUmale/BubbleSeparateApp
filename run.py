import os
from app import create_app

# --- Main Application Execution ---
if __name__ == '__main__':
    # Ensure the 'static' directory exists
    if not os.path.exists('static'):
        os.makedirs('static')

    # Create the Flask app and SocketIO instance using the application factory
    app, socketio = create_app()

    # Run the application
    # use_reloader=False is important for preventing the background threads from running twice
    print("Starting Flask server with Socket.IO on port 8080...")
    socketio.run(app, debug=True, use_reloader=False, allow_unsafe_werkzeug=True, port=8080)