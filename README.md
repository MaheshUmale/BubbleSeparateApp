# Real-Time Market Data Visualizer

This web application provides a real-time visualization of stock market data, allowing users to monitor price movements, trading volumes, and significant trade events through an interactive bubble chart. The application is built with Python, Flask, and Socket.IO on the backend, and it uses ECharts on the frontend for high-performance data visualization.

## Key Features

- **Upstox Integration**: Securely log in using your Upstox account to access live market data.
- **Dynamic Subscriptions**: The application automatically detects and subscribes to new trading symbols from `BBSCAN` files, ensuring you always have the latest data.
- **Interactive Charting**: The chart is built with ECharts and includes features like:
  - **Candlestick View**: Displays the open, high, low, and close prices for a selected time interval.
  - **Volume Bars**: Visualize normal and "big player" trading volumes.
  - **Bubble-Chart Overlay**: Highlights significant trading volumes as bubbles on the price chart.
- **Client-Side Optimization**: The application is optimized for performance by processing data on the client-side, which minimizes server load and provides a smooth, responsive user experience.
- **Modular Architecture**: The backend is built with a modular design, making it easy to maintain and extend.

## How It Works

The application's backend is a Flask web server that uses the Upstox API to stream live market data over a WebSocket connection. When a user logs in, the server establishes a connection and begins subscribing to a list of trading instruments. As new data arrives, it is broadcast to the frontend via Socket.IO.

The frontend is a single-page application that receives the live data and renders it in real-time using the ECharts library. The chart is highly interactive, allowing users to zoom, pan, and adjust various parameters to customize the visualization.

## Setup and Installation

To run the application locally, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a Configuration File**:
   - Create a file named `my.properties` in the root of the project.
   - Add your Upstox API credentials to this file in the following format:
     ```ini
     [DEFAULT]
     apikey = YOUR_API_KEY
     secret = YOUR_API_SECRET
     ```

3. **Install Dependencies**:
   - It is recommended to use a virtual environment to manage dependencies.
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   python run.py
   ```
   - The application will be available at `http://127.0.0.1:8080`.

## Usage

- **Login**: Open the application in your browser and click the "Login with Upstox" button to authenticate.
- **Select a Security**: Once logged in, use the dropdown menu to select a security to monitor.
- **Adjust Parameters**: Use the controls to change the candle interval, bubble threshold, and "big player" quantity to customize the chart to your preferences.

This project is designed to be a powerful tool for traders and market analysts who need to visualize and react to market data in real-time. With its modular design and optimized performance, it serves as a solid foundation for further development and customization.