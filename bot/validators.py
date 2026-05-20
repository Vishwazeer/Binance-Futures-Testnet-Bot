from decimal import Decimal, InvalidOperation

VALID_SYMBOLS = {"BTCUSDT", "ETHUSDT", "BNBUSDT"}
VALID_SIDES   = {"BUY", "SELL"}
VALID_TYPES   = {"MARKET", "LIMIT", "STOP_MARKET"}

def validate_inputs(symbol: str, side: str, order_type: str, quantity: float | str, price: float | str | None):
    # Case-insensitive validation but raise standardized uppercase strings
    sym = symbol.upper()
    sid = side.upper()
    ot = order_type.upper()

    if sym not in VALID_SYMBOLS:
        raise ValueError(f"Unknown symbol '{symbol}'. Supported: {sorted(list(VALID_SYMBOLS))}")
        
    if sid not in VALID_SIDES:
        raise ValueError(f"Side must be BUY or SELL, got '{side}'")
        
    if ot not in VALID_TYPES:
        raise ValueError(f"Order type '{order_type}' not supported. Supported: {sorted(list(VALID_TYPES))}")

    try:
        qty = Decimal(str(quantity))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"Invalid quantity: '{quantity}'")
        
    if qty <= 0:
        raise ValueError("Quantity must be greater than 0")

    if ot in {"LIMIT", "STOP_MARKET"} and price is None:
        raise ValueError(f"Price is required for {ot} orders")

    if price is not None:
        try:
            p = Decimal(str(price))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError(f"Invalid price: '{price}'")
            
        if p <= 0:
            raise ValueError("Price must be greater than 0")
