# Binance Futures Testnet Trading Bot CLI

An aesthetic, high-performance terminal trading bot designed for the **Binance Futures Testnet**. Built using Python with a robust multi-handler logger, input validation, HMAC query-string signing, and a premium navy-dark fintech terminal interface powered by `Typer` and `Rich`.

---

## Technical Features & Highlights

1. **Modern Binance API Integration**: Implements the latest **December 2025 Binance Migration** which routes conditional orders (`STOP_MARKET`) to the mandatory dedicated **Algo Order Service** (`/fapi/v1/algoOrder`), automatically bridging response payloads to standard order receipt fields.
2. **Fail-Fast Validation**: Intercepts incorrect trading symbols, side directions, order types, negative quantities, or missing limit/stop prices on the client side before issuing signed requests.
3. **Dual File Logging**:
   - `logs/trading.log`: Stores comprehensive historical diagnostic data (`DEBUG` and up).
   - `logs/errors.log`: Stores all HTTP exceptions, connection problems, and validation errors (`ERROR` and up).
4. **Navy-Dark Terminal Theme**: Customized UI styled with HSL harmonized navy-dark tokens for values, order tags, status indicators, and success borders.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          ← Signed HMAC REST wrapper (handles standard & algo endpoints)
│   ├── orders.py          ← order placement & logging orchestration
│   ├── validators.py      ← fail-fast client input validation
│   ├── theme.py           ← custom navy-dark console stylesheet
│   └── logging_config.py  ← multi-handler file + stdout log configuration
├── logs/
│   ├── trading.log        ← persistent diagnostic actions (DEBUG+)
│   └── errors.log         ← persistent execution failures (ERROR+)
├── cli.py                 ← Typer command-line entry point
├── .env                   ← Git-ignored local API credentials
├── .env.example           ← Local environment variables template
├── README.md              ← Setup and user instruction guide
└── requirements.txt       ← Pin python package dependencies
```

---

## Installation & Setup

### Prerequisites
* Python 3.10 or higher.
* Active API keys generated from [testnet.binancefuture.com](https://testnet.binancefuture.com).

### 1. Clone & Initialize Directory
Ensure the directory structure matches the layout above. Open your terminal in the root folder.

### 2. Set Up Virtual Environment
Create and activate a local Python virtual environment:

**On Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Pin Dependencies
Install the required system modules:
```bash
pip install -r requirements.txt
```

### 4. Configure Credentials
Copy `.env.example` to `.env` and fill in your Binance Futures Testnet API Key and Secret:
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```
Inside `.env`:
```ini
API_KEY=your_actual_binance_testnet_api_key
API_SECRET=your_actual_binance_testnet_api_secret
```

---

## CLI Usage Instructions

To view options and commands, run:
```bash
python cli.py --help
```

### 1. Test Connection
Ping the Binance Futures Testnet to verify API keys and network latency:
```bash
python cli.py ping
```

### 2. Place a Market Buy Order
Instantly execute a `BUY` order of `0.001` BTC:
```bash
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### 3. Place a Limit Sell Order
Register a `SELL` order of `0.01` ETH at `3200.0` USDT:
```bash
python cli.py order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 3200
```

### 4. Place a Stop-Market Order (Algo Order)
Register a stop-loss trigger at `58000.0` for `0.001` BTC:
```bash
python cli.py order --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --price 58000
```
*Note: Under the hood, this order utilizes `/fapi/v1/algoOrder` to comply with current Binance rules.*

---

## Troubleshooting & Verification

* **Invalid API Credentials**: If you see `[!] API Credentials Missing`, verify that `.env` is located in the same directory where you execute the CLI, and that the values match those on the Binance Testnet dashboard.
* **Insufficient Margin**: If orders fail with HTTP status `400`, verify your testnet account balance. Go to [testnet.binancefuture.com](https://testnet.binancefuture.com) and click **Faucet** to fund your account.
* **Logs Directory**: All requests are appended to `logs/trading.log`. You can tail the log to watch interactions in real-time.
