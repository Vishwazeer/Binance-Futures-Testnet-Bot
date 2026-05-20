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

@app.route("/api/account", methods=["GET"])
def get_account_details():
    """Fetches balance, non-zero assets, and open positions from Binance."""
    try:
        client = get_client()
        data = client.get_account_info()
        
        # Filter assets with positive balances or active margins
        assets = []
        for a in data.get("assets", []):
            wallet_bal = float(a.get("walletBalance", 0))
            unrealized_pnl = float(a.get("unrealizedProfit", 0))
            available_bal = float(a.get("availableBalance", 0))
            if wallet_bal > 0 or unrealized_pnl != 0 or available_bal > 0:
                assets.append({
                    "asset": a.get("asset"),
                    "walletBalance": wallet_bal,
                    "unrealizedProfit": unrealized_pnl,
                    "availableBalance": available_bal,
                })
                
        # Filter active positions (positionAmt != 0)
        positions = []
        for p in data.get("positions", []):
            amt = float(p.get("positionAmt", 0))
            if amt != 0:
                positions.append({
                    "symbol": p.get("symbol"),
                    "positionAmt": amt,
                    "entryPrice": float(p.get("entryPrice", 0)),
                    "unrealizedProfit": float(p.get("unrealizedProfit", 0)),
                    "leverage": int(p.get("leverage", 20)),
                    "isolated": p.get("isolated", False)
                })
                
        return jsonify({
            "status": "success",
            "walletBalance": float(data.get("totalWalletBalance", 0)),
            "marginBalance": float(data.get("totalMarginBalance", 0)),
            "availableBalance": float(data.get("availableBalance", 0)),
            "unrealizedProfit": float(data.get("totalUnrealizedProfit", 0)),
            "assets": assets,
            "positions": positions
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to fetch account info: {str(e)}"}), 500

@app.route("/api/tickers", methods=["GET"])
def get_tickers():
    """Fetches public market ticker prices for dashboard display."""
    try:
        client = get_client()
        tickers = client.get_ticker_prices()
        # Filter only our valid symbols
        valid_symbols = {"BTCUSDT", "ETHUSDT", "BNBUSDT"}
        prices = {}
        for t in tickers:
            sym = t.get("symbol")
            if sym in valid_symbols:
                prices[sym] = float(t.get("price", 0))
        return jsonify({"status": "success", "prices": prices})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/leverage", methods=["POST"])
def adjust_leverage():
    """Adjusts position leverage for a specific asset symbol."""
    try:
        client = get_client()
        data = request.get_json() or {}
        symbol = data.get("symbol", "").upper()
        leverage = data.get("leverage")
        
        if not symbol or not leverage:
            return jsonify({"status": "error", "message": "Symbol and leverage are required."}), 400
            
        try:
            leverage = int(leverage)
        except ValueError:
            return jsonify({"status": "error", "message": "Leverage must be a valid integer."}), 400
            
        if leverage < 1 or leverage > 125:
            return jsonify({"status": "error", "message": "Leverage must be between 1 and 125."}), 400

        result = client.change_leverage(symbol, leverage)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Leverage adjustment failed: {str(e)}"}), 500

@app.route("/api/close_position", methods=["POST"])
def close_active_position():
    """Finds active position size and submits offsetting Market order to flat it."""
    try:
        client = get_client()
        data = request.get_json() or {}
        symbol = data.get("symbol", "").upper()
        
        if not symbol:
            return jsonify({"status": "error", "message": "Symbol is required to close a position."}), 400
            
        # 1. Fetch current positions to find size
        account_data = client.get_account_info()
        target_pos = None
        for p in account_data.get("positions", []):
            if p.get("symbol", "").upper() == symbol:
                target_pos = p
                break
                
        if not target_pos:
            return jsonify({"status": "error", "message": f"No position record found for {symbol}."}), 400
            
        position_amt = float(target_pos.get("positionAmt", 0))
        if position_amt == 0:
            return jsonify({"status": "error", "message": f"No active position exists for {symbol} (size is 0)."}), 400
            
        # 2. Determine offsetting side and absolute size
        offsetting_side = "SELL" if position_amt > 0 else "BUY"
        absolute_qty = abs(position_amt)
        
        logger.info("GUI initiating closing market order for %s: %s %s", symbol, offsetting_side, absolute_qty)
        
        # 3. Place standard offsetting MARKET order
        result = place_order(client, symbol, offsetting_side, "MARKET", absolute_qty)
        return jsonify({"status": "success", "message": f"Position closed successfully.", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to close position: {str(e)}"}), 500

@app.route("/api/open_orders", methods=["GET"])
def get_open_orders_list():
    """Aggregates all pending standard and algorithmic/stop orders."""
    try:
        client = get_client()
        
        # Fetch standard open orders
        std_orders = []
        try:
            std_orders = client.get_open_orders()
        except Exception as e:
            logger.error("Error fetching open standard orders: %s", e)
            
        # Fetch open algo orders
        algo_orders = []
        try:
            algo_orders = client.get_open_algo_orders()
        except Exception as e:
            logger.error("Error fetching open algo orders: %s", e)
            
        formatted_orders = []
        
        # Map standard open orders
        for o in std_orders:
            formatted_orders.append({
                "orderId": o.get("orderId"),
                "symbol": o.get("symbol"),
                "side": o.get("side"),
                "type": o.get("type"),
                "price": float(o.get("price", 0)),
                "quantity": float(o.get("origQty", 0)),
                "isAlgo": False,
                "status": o.get("status")
            })
            
        # Map algorithmic orders (STOP_MARKET etc.)
        for o in algo_orders:
            formatted_orders.append({
                "orderId": o.get("algoId"),
                "symbol": o.get("symbol"),
                "side": o.get("side"),
                "type": o.get("type"),
                "price": float(o.get("triggerPrice", 0)),
                "quantity": float(o.get("quantity", 0)),
                "isAlgo": True,
                "status": o.get("status", "NEW (ALGO)")
            })
            
        return jsonify({"status": "success", "orders": formatted_orders})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to fetch open orders: {str(e)}"}), 500

@app.route("/api/cancel_order", methods=["POST"])
def cancel_pending_order():
    """Cancels a standard or algorithmic pending order by ID."""
    try:
        client = get_client()
        data = request.get_json() or {}
        symbol = data.get("symbol", "").upper()
        order_id = data.get("orderId")
        is_algo = data.get("isAlgo", False)
        
        if not symbol or not order_id:
            return jsonify({"status": "error", "message": "Symbol and orderId are required."}), 400
            
        if is_algo:
            result = client.cancel_algo_order(symbol, order_id)
        else:
            result = client.cancel_order(symbol, order_id)
            
        return jsonify({"status": "success", "message": "Order cancelled successfully.", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to cancel order: {str(e)}"}), 500

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
