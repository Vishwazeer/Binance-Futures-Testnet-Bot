import time
import hmac
import hashlib
import requests
from typing import Any
from .logging_config import setup_logging

BASE_URL = "https://testnet.binancefuture.com"
logger = setup_logging()

class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": api_key})

    def _sign(self, params: dict) -> dict:
        # Clone params to avoid modifying original dictionary
        signed_params = params.copy()
        signed_params["timestamp"] = int(time.time() * 1000)
        
        # Sort and join params to construct valid query string
        query = "&".join(f"{k}={v}" for k, v in signed_params.items())
        
        # Calculate HMAC signature
        signed_params["signature"] = hmac.new(
            self.api_secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        return signed_params

    def ping(self) -> bool:
        """Pings the Binance Futures Testnet server to verify connection."""
        endpoint = f"{BASE_URL}/fapi/v1/ping"
        logger.debug("REQUEST → GET %s", endpoint)
        try:
            resp = self.session.get(endpoint, timeout=10)
            resp.raise_for_status()
            logger.debug("RESPONSE ← OK (status: %d)", resp.status_code)
            return True
        except requests.RequestException as e:
            logger.error("Ping connectivity test failed: %s", e)
            return False

    def place_order(self, **params) -> dict[str, Any]:
        """Places a signed order on the Binance Futures Testnet."""
        order_type = params.get("type", "").upper()
        
        if order_type == "STOP_MARKET":
            endpoint = f"{BASE_URL}/fapi/v1/algoOrder"
            algo_params = {
                "algoType": "CONDITIONAL",
                "symbol": params["symbol"],
                "side": params["side"],
                "type": "STOP_MARKET",
                "triggerPrice": params["stopPrice"],
                "quantity": params["quantity"]
            }
            signed = self._sign(algo_params)
        else:
            endpoint = f"{BASE_URL}/fapi/v1/order"
            signed = self._sign(params)

        logger.debug("REQUEST → POST %s | params=%s", endpoint, params)
        try:
            resp = self.session.post(endpoint, params=signed, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            if order_type == "STOP_MARKET":
                # Bridge the response to standard fields for unified display and logging
                mapped_data = {
                    "orderId": data.get("algoId"),
                    "clientOrderId": data.get("clientAlgoId"),
                    "symbol": params["symbol"],
                    "side": params["side"],
                    "type": params["type"],
                    "status": "NEW (ALGO)",
                    "executedQty": "0.000",
                    "avgPrice": "0.00"
                }
                logger.debug("RESPONSE ← (MAPPED ALGO) %s", mapped_data)
                return mapped_data

            logger.debug("RESPONSE ← %s", data)
            return data
        except requests.HTTPError as e:
            logger.error("HTTP error: %s | body: %s", e, e.response.text)
            try:
                err_json = e.response.json()
                if "msg" in err_json:
                    msg = err_json["msg"]
                    code = err_json.get("code", "N/A")
                    raise Exception(f"Exchange rejected order: {msg} (Code {code})") from e
            except (ValueError, TypeError, KeyError):
                pass
            raise
        except requests.RequestException as e:
            logger.error("Network error: %s", e)
            raise

    def get_account_info(self) -> dict[str, Any]:
        """Fetches comprehensive account details, assets, and positions."""
        endpoint = f"{BASE_URL}/fapi/v2/account"
        signed = self._sign({})
        logger.debug("REQUEST → GET %s", endpoint)
        try:
            resp = self.session.get(endpoint, params=signed, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            logger.debug("RESPONSE ← Account details loaded successfully.")
            return data
        except requests.RequestException as e:
            logger.error("Failed to fetch account info: %s", e)
            raise

    def change_leverage(self, symbol: str, leverage: int) -> dict[str, Any]:
        """Changes the leverage setting for a symbol."""
        endpoint = f"{BASE_URL}/fapi/v1/leverage"
        params = {"symbol": symbol.upper(), "leverage": int(leverage)}
        signed = self._sign(params)
        logger.info("Changing leverage for %s to %dx", symbol, leverage)
        try:
            resp = self.session.post(endpoint, params=signed, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            logger.debug("Leverage response: %s", data)
            return data
        except requests.RequestException as e:
            logger.error("Failed to change leverage: %s", e)
            raise

    def get_open_orders(self, symbol: str | None = None) -> list[dict[str, Any]]:
        """Fetches currently open standard orders."""
        endpoint = f"{BASE_URL}/fapi/v1/openOrders"
        params = {}
        if symbol:
            params["symbol"] = symbol.upper()
        signed = self._sign(params)
        logger.debug("Fetching open standard orders...")
        try:
            resp = self.session.get(endpoint, params=signed, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error("Failed to fetch open standard orders: %s", e)
            raise

    def get_open_algo_orders(self, symbol: str | None = None) -> list[dict[str, Any]]:
        """Fetches pending algorithmic/conditional orders (e.g. STOP_MARKET)."""
        endpoint = f"{BASE_URL}/fapi/v1/apiPendingOrders"
        params = {}
        if symbol:
            params["symbol"] = symbol.upper()
        signed = self._sign(params)
        logger.debug("Fetching open algo orders...")
        try:
            resp = self.session.get(endpoint, params=signed, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict):
                return data.get("orders", [])
            return data
        except requests.RequestException as e:
            logger.error("Failed to fetch open algo orders: %s", e)
            return []

    def cancel_order(self, symbol: str, order_id: int) -> dict[str, Any]:
        """Cancels a pending standard order."""
        endpoint = f"{BASE_URL}/fapi/v1/order"
        params = {"symbol": symbol.upper(), "orderId": int(order_id)}
        signed = self._sign(params)
        logger.info("Canceling order %d for %s", order_id, symbol)
        try:
            resp = self.session.delete(endpoint, params=signed, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error("Failed to cancel order: %s", e)
            raise

    def cancel_algo_order(self, symbol: str, algo_id: int) -> dict[str, Any]:
        """Cancels a pending algorithmic/conditional order."""
        endpoint = f"{BASE_URL}/fapi/v1/algoOrder"
        params = {"symbol": symbol.upper(), "algoId": int(algo_id)}
        signed = self._sign(params)
        logger.info("Canceling algo order %d for %s", algo_id, symbol)
        try:
            resp = self.session.delete(endpoint, params=signed, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error("Failed to cancel algo order: %s", e)
            raise

    def get_ticker_prices(self) -> list[dict[str, Any]]:
        """Fetches current mark/ticker prices for all pairs."""
        endpoint = f"{BASE_URL}/fapi/v1/ticker/price"
        logger.debug("Fetching current ticker prices...")
        try:
            resp = self.session.get(endpoint, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error("Failed to fetch ticker prices: %s", e)
            raise

