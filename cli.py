import os
import sys
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from dotenv import load_dotenv

from bot.client import BinanceClient
from bot.orders import place_order
from bot.theme import TRADING_THEME

# 1. Load environment variables
load_dotenv()

# 2. Initialize Typer and custom theme Rich Console
app = typer.Typer(
    help="Binance Futures Testnet Trading Bot — Premium Terminal UI Command Line Utility",
    no_args_is_help=True
)
console = Console(theme=TRADING_THEME)

def get_client() -> BinanceClient:
    """Helper to load API credentials and return BinanceClient or exit if unconfigured."""
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    
    if not api_key or not api_secret or api_key == "your_binance_testnet_api_key" or api_secret == "your_binance_testnet_api_secret":
        console.print(Panel(
            "[warning][!] API Credentials Missing or Using Placeholders![/]\n\n"
            "[muted]To fix this:\n"
            "1. Copy [value].env.example[/] to [value].env[/]\n"
            "2. Configure [accent]API_KEY[/] and [accent]API_SECRET[/] from [accent]testnet.binancefuture.com[/][/]",
            title="[error]Configuration Required[/]",
            border_style="warning",
            padding=(1, 2)
        ))
        raise typer.Exit(1)
        
    return BinanceClient(api_key, api_secret)

@app.command(name="ping")
def ping_api():
    """Diagnostic command to check connectivity to the Binance Futures Testnet."""
    console.print("[accent]>>> Checking connectivity to Binance Futures Testnet...[/]")
    try:
        client = get_client()
        success = client.ping()
        if success:
            console.print(Panel(
                "[success][OK] Connection test succeeded![/]\n"
                "[muted]Binance Futures Testnet is reachable and API credentials format is valid.[/]",
                title="[success]Status Online[/]",
                border_style="success",
                padding=(1, 2)
            ))
        else:
            console.print(Panel(
                "[error][x] Ping request completed but server returned an unhealthy response.[/]",
                title="[error]Status Unhealthy[/]",
                border_style="error",
                padding=(1, 2)
            ))
            raise typer.Exit(1)
    except typer.Exit:
        raise
    except Exception as e:
        console.print(Panel(
            f"[error][x] Unexpected connection error occurred:[/]\n[muted]{e}[/]",
            title="[error]Status Error[/]",
            border_style="error",
            padding=(1, 2)
        ))
        raise typer.Exit(1)

@app.command(name="order")
def execute_order(
    symbol: str = typer.Option(..., "--symbol", "-s", help="Trading pair, e.g. BTCUSDT, ETHUSDT, BNBUSDT"),
    side: str = typer.Option(..., "--side", "-d", help="Order side: BUY or SELL"),
    order_type: str = typer.Option(..., "--type", "-t", help="Order type: MARKET, LIMIT, or STOP_MARKET"),
    quantity: float = typer.Option(..., "--quantity", "-q", help="The asset quantity to trade"),
    price: float = typer.Option(None, "--price", "-p", help="Target price (required for LIMIT / STOP_MARKET)")
):
    """Places an order (MARKET, LIMIT, or STOP_MARKET) on the Binance Futures Testnet."""
    try:
        client = get_client()
    except typer.Exit:
        raise

    # Pre-render inputs summary
    t = Table(title="[accent]ORDER CONFIGURATION[/]", show_header=False, box=None, padding=(0, 2))
    
    # Render Side tag with specific coloring
    side_val = f"[buy]{side.upper()}[/]" if side.upper() == "BUY" else f"[sell]{side.upper()}[/]"
    type_val = f"[value]{order_type.upper()}[/]"
    price_val = f"[value]{price}[/]" if price is not None else "[dimmed]- (MARKET)[/]"

    t.add_row("[muted]Symbol[/]", f"[value]{symbol.upper()}[/]")
    t.add_row("[muted]Side[/]", side_val)
    t.add_row("[muted]Type[/]", type_val)
    t.add_row("[muted]Quantity[/]", f"[value]{quantity}[/]")
    t.add_row("[muted]Price[/]", price_val)

    console.print(Panel(t, border_style="border", subtitle="[dimmed]Validation Pending[/]"))

    try:
        # Place order via our module
        result = place_order(client, symbol, side, order_type, quantity, price)
        
        # Display Success Receipt
        console.print()
        console.print(Panel(
            "[success][OK] Order executed successfully on Binance Futures Testnet[/]",
            border_style="success",
            padding=(0, 2)
        ))

        # Receipt Table details
        r = Table(title="[accent]EXECUTION RECEIPT[/]", show_header=False, box=None, padding=(0, 2))
        
        # Gather relevant fields from API response
        receipt_fields = {
            "Order ID": "orderId",
            "Client Order ID": "clientOrderId",
            "Symbol": "symbol",
            "Side": "side",
            "Type": "type",
            "Status": "status",
            "Executed Qty": "executedQty",
            "Avg Price": "avgPrice",
        }

        for label, key in receipt_fields.items():
            if key in result:
                val = str(result[key])
                # Color code specific keys
                if key == "side":
                    val = f"[buy]{val}[/]" if val == "BUY" else f"[sell]{val}[/]"
                elif key == "status":
                    val = f"[success]{val}[/]" if val == "NEW" or val == "FILLED" else f"[warning]{val}[/]"
                elif key in {"orderId", "executedQty", "avgPrice"}:
                    val = f"[value]{val}[/]"
                
                r.add_row(f"[muted]{label}[/]", val)
                
        console.print(Panel(r, border_style="border"))

    except ValueError as e:
        console.print()
        console.print(Panel(
            f"[error][x] Input validation check failed[/]\n\n[warning]{e}[/]",
            title="[error]Validation Error[/]",
            border_style="error",
            padding=(1, 2)
        ))
        raise typer.Exit(1)
    except typer.Exit:
        raise
    except Exception as e:
        console.print()
        console.print(Panel(
            f"[error][x] Order submission failed[/]\n\n[muted]{e}[/]",
            title="[error]Execution Failure[/]",
            border_style="error",
            padding=(1, 2)
        ))
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
