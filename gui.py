import os
import sys
import webbrowser
from threading import Timer
from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv

from bot.client import BinanceClient
from bot.orders import place_order
from bot.logging_config import setup_logging

# Load local environment variables
load_dotenv()
logger = setup_logging()

app = Flask(__name__, template_folder="templates")

def get_client() -> BinanceClient:
    """Helper to instantiate the Binance API client using .env configuration."""
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    
    if (not api_key 
        or not api_secret 
        or api_key == "your_binance_testnet_api_key" 
        or api_secret == "your_binance_testnet_api_secret"):
        raise ValueError("Binance API credentials missing or incomplete. Please populate .env file with active Testnet keys.")
        
    return BinanceClient(api_key, api_secret)

@app.route("/")
def home():
    """Serves the Single Page Application Trading Dashboard."""
    return render_template("index.html")

@app.route("/api/ping", methods=["GET"])
def ping_status():
    """Diagnostic REST API to verify exchange connectivity."""
    try:
        client = get_client()
        success = client.ping()
        if success:
            return jsonify({
                "status": "healthy",
                "message": "Connection test succeeded! Binance Futures Testnet is online."
            })
        else:
            return jsonify({
                "status": "unhealthy",
                "message": "Ping request completed but server returned an unhealthy status."
            }), 400
    except ValueError as e:
        return jsonify({"status": "config_error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Connection test failed: {str(e)}"}), 500

@app.route("/api/order", methods=["POST"])
def place_new_order():
    """Validates parameters, submits signed trade request, and returns confirmation receipt."""
    try:
        client = get_client()
        data = request.get_json() or {}
        
        symbol = data.get("symbol", "").upper()
        side = data.get("side", "").upper()
        order_type = data.get("type", "").upper()
        quantity = data.get("quantity")
        price = data.get("price")
        
        # Convert empty input values to None
        if price == "" or price is None:
            price = None
        else:
            try:
                price = float(price)
            except ValueError:
                return jsonify({"status": "error", "message": f"Invalid price format: '{price}'"}), 400
                
        if quantity == "" or quantity is None:
            return jsonify({"status": "error", "message": "Quantity is a required field."}), 400
            
        try:
            quantity = float(quantity)
        except ValueError:
            return jsonify({"status": "error", "message": f"Invalid quantity format: '{quantity}'"}), 400

        # Invoke core bot execution logic (logging and fail-fast validators run here)
        result = place_order(client, symbol, side, order_type, quantity, price)
        return jsonify({"status": "success", "data": result})
        
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Order execution failed: {str(e)}"}), 500

def open_browser():
    """Autolaunches the user's default browser to localhost."""
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    # Autolaunch the browser in 1.5 seconds.
    # WERKZEUG_RUN_MAIN is set by Flask's auto-reloader; checking it prevents launching the browser twice.
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        Timer(1.5, open_browser).start()
        
    logger.info("Starting local GUI server at http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
