from .client import BinanceClient
from .validators import validate_inputs
from .logging_config import setup_logging

logger = setup_logging()

def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None,
    time_in_force: str = "GTC"
) -> dict:
    sym = symbol.upper()
    sid = side.upper()
    ot = order_type.upper()
    
    # 1. Perform fail-fast validation checks
    validate_inputs(sym, sid, ot, quantity, price)

    # 2. Build parameters for standard or stop order types
    params = dict(symbol=sym, side=sid, type=ot, quantity=quantity)
    if ot == "LIMIT":
        params.update(price=price, timeInForce=time_in_force)
    elif ot == "STOP_MARKET":
        params["stopPrice"] = price

    # 3. Log actions to file and console
    logger.info(
        "Placing %s %s order | symbol=%s qty=%s price=%s",
        sid, ot, sym, quantity, price if price is not None else "MARKET"
    )
    
    # 4. Invoke API request
    result = client.place_order(**params)
    
    # 5. Log confirmation receipts
    logger.info(
        "Order placed | id=%s status=%s",
        result.get("orderId"), result.get("status")
    )
    
    return result
