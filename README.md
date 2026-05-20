# Binance Futures Testnet Trading Bot

A premium, full-featured local trading bot and interactive web dashboard designed for the **Binance Futures Testnet**. Built with Python, featuring a modern Flask Web GUI with live market data, real-time portfolio tracking, and a powerful Rich-themed CLI — all running securely on your local machine.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0+-green?style=flat-square&logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Testnet](https://img.shields.io/badge/Binance-Futures%20Testnet-orange?style=flat-square&logo=binance&logoColor=white)

---

## ✨ Features at a Glance

| Feature | GUI | CLI |
|---|:---:|:---:|
| Place Market / Limit / Stop-Market Orders | ✅ | ✅ |
| Live Price Tickers (BTC, ETH, BNB) | ✅ | — |
| Portfolio & Wallet Balance View | ✅ | — |
| Active Positions with Unrealized PnL | ✅ | — |
| One-Click Close Position | ✅ | — |
| Adjust Leverage (1x – 125x) | ✅ | — |
| View & Cancel Pending Orders | ✅ | — |
| Connection Health Check (Ping) | ✅ | ✅ |
| Algo Order Support (Stop-Market) | ✅ | ✅ |
| Beautiful Dark Theme UI | ✅ | ✅ |
| Dual File Logging (Debug + Errors) | ✅ | ✅ |

---

## 📁 Project Structure

```
Binance Trading Bot/
├── bot/
│   ├── __init__.py          # Package initializer
│   ├── client.py            # Signed HMAC REST wrapper (standard + algo endpoints)
│   ├── orders.py            # Order placement & logging orchestration
│   ├── validators.py        # Fail-fast client-side input validation
│   ├── theme.py             # Custom navy-dark Rich console stylesheet
│   └── logging_config.py    # Multi-handler file + stdout log configuration
├── templates/
│   └── index.html           # Web GUI Dashboard (Single Page Application)
├── logs/
│   ├── trading.log          # All diagnostic actions (DEBUG level and up)
│   └── errors.log           # Execution failures only (ERROR level and up)
├── cli.py                   # Typer-powered command-line entry point
├── gui.py                   # Local Flask web server & auto browser launcher
├── .env                     # Your API credentials (git-ignored, never pushed)
├── .env.example             # Template showing required environment variables
├── requirements.txt         # Python package dependencies
└── README.md                # This file
```

---

## 🚀 Installation & Setup (Step by Step)

### Prerequisites

- **Python 3.10** or higher installed on your system
- A **Binance Futures Testnet** account with API keys

### Step 1 — Get Your API Keys

1. Go to [testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with your GitHub account
3. Click **"API Key"** in the top navigation
4. Click **"Create API Key"** — copy both the **API Key** and the **Secret Key**
5. Keep these safe — you'll need them in Step 4

### Step 2 — Clone the Repository

```bash
git clone https://github.com/Vishwazeer/Binance-Futures-Testnet-Bot.git
cd Binance-Futures-Testnet-Bot
```

### Step 3 — Create & Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

> 💡 You should see `(.venv)` appear at the beginning of your terminal prompt. This means the virtual environment is active.

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs: `requests`, `flask`, `typer`, `rich`, and `python-dotenv`.

### Step 5 — Configure Your API Keys

Copy the template file and fill in your actual keys:

**Windows:**
```powershell
copy .env.example .env
```

**macOS / Linux:**
```bash
cp .env.example .env
```

Now open `.env` in any text editor and replace the placeholder values:

```ini
API_KEY=paste_your_actual_api_key_here
API_SECRET=paste_your_actual_secret_key_here
```

> 🔒 **Security Note:** The `.env` file is listed in `.gitignore` and will **never** be uploaded to GitHub. Your keys stay on your local machine only.

---

## 🖥️ How to Use — Web GUI (Recommended for Beginners)

The Web GUI is the easiest way to use the bot. It runs a local web page in your browser — no coding needed.

### Starting the GUI

```bash
python gui.py
```

Your default browser will automatically open to `http://127.0.0.1:5000`. If it doesn't, manually open that URL.

> To stop the server, press `Ctrl + C` in your terminal.

---

### GUI Walkthrough — What You'll See

#### 1️⃣ Header & Connection Status

At the very top you'll see:
- **"Binance Futures Desk"** — the app title
- A **status indicator** (dot + label) showing `ONLINE`, `OFFLINE`, or `CHECKING...`
- A **"Test Connection"** link — click it anytime to manually verify the exchange connection

#### 2️⃣ Live Price Tickers Ribbon

Right below the header is a horizontal ribbon showing **real-time prices** for:
- **BTCUSDT** (Bitcoin)
- **ETHUSDT** (Ethereum)
- **BNBUSDT** (Binance Coin)

Each ticker updates every **3 seconds** and shows:
- A **green ▲ arrow** when the price goes up
- A **red ▼ arrow** when the price goes down

#### 3️⃣ Portfolio & Live Positions (Top Panel)

This section shows your **live account data**, auto-refreshing every **10 seconds**:

**Stats Cards:**
| Card | What It Shows |
|---|---|
| Wallet Balance | Total USDT in your account |
| Margin Balance | USDT allocated as margin for open trades |
| Available Balance | USDT available to open new trades |
| Unrealized PnL | Profit or loss on currently open positions (green = profit, red = loss) |

**Asset Balances Table:**
Shows each coin/token you hold with its wallet balance, available balance, and unrealized PnL.

**Active Positions Table:**
Shows every open trade with:
| Column | Meaning |
|---|---|
| Symbol | The trading pair (e.g. BTCUSDT) |
| Size | Direction (BUY/SELL) and quantity |
| Entry Price | The price at which you entered the trade |
| Unrealized PnL | Current profit/loss (green = profit, red = loss) |
| Leverage | Current leverage multiplier (e.g. 20x) |
| Action | A red **CLOSE** button to instantly close the position |

**How to Close a Position:**
1. Find the position you want to close in the table
2. Click the red **CLOSE** button
3. A confirmation dialog will appear — click **OK** to confirm
4. The bot automatically places an offsetting market order to flatten your position
5. Your balances and positions will refresh immediately

**Pending & Trigger Orders Table:**
Shows all open limit orders and stop-market trigger orders with:
- Symbol, Side (BUY/SELL), Type, Price, Quantity
- Whether it's a **STANDARD** or **ALGO (Stop)** order
- Current status
- An amber **CANCEL** button to remove the order

**How to Cancel a Pending Order:**
1. Find the order in the table
2. Click the amber **CANCEL** button
3. Confirm the cancellation in the dialog
4. The order is removed from the exchange

#### 4️⃣ Order Dispatcher (Left Panel)

This is where you **place new trades**. Fill in the form fields:

| Field | How to Use |
|---|---|
| **Order Side** | Click **BUY** (green) to go long, or **SELL** (red) to go short |
| **Asset Pair** | Select from the dropdown: BTCUSDT, ETHUSDT, or BNBUSDT |
| **Target Leverage** | Type a number from 1 to 125 and click **SET** to change leverage for the selected symbol |
| **Order Type** | Choose: **MARKET** (instant fill), **LIMIT** (fill at your price), or **STOP_MARKET** (trigger when price hits your level) |
| **Quantity** | Enter the amount to trade (e.g. `0.001` for BTC) |
| **Price** | Only appears for LIMIT and STOP_MARKET orders — enter your target price |

Then click the blue **Place Order** button. The button shows a spinner while processing.

#### 5️⃣ Order Receipt (Right Panel)

After placing an order, a **ticket receipt** appears showing:
- Order ID
- Symbol, Side, Type
- Execution status (FILLED for market orders, NEW for pending orders)
- Client Order ID

If there's an error (e.g. insufficient margin), a **red error box** appears with the exchange's error message.

#### 6️⃣ Manual Sync

Click the **🔄 sync button** next to the portfolio header to force an immediate refresh of all data.

---

### GUI Quick Examples

**Example 1 — Buy 0.001 BTC at market price:**
1. Click **BUY**
2. Select **BTCUSDT**
3. Set Order Type to **MARKET**
4. Type `0.001` in Quantity
5. Click **Place Order**

**Example 2 — Set 10x leverage and place a limit sell:**
1. Select **ETHUSDT** from the Asset Pair dropdown
2. Type `10` in the leverage input, click **SET**
3. Click **SELL**
4. Set Order Type to **LIMIT**
5. Type `0.01` in Quantity
6. Type `5000` in Price
7. Click **Place Order**

**Example 3 — Close an open position:**
1. Scroll to the Active Positions table
2. Find the position you want to close
3. Click the red **CLOSE** button → Confirm

---

## ⌨️ How to Use — Command Line (CLI)

The CLI is for power users who prefer working in the terminal. It uses `Typer` + `Rich` for a beautiful navy-dark themed output.

### View All Available Commands

```bash
python cli.py --help
```

This displays the full list of commands with descriptions.

---

### Command 1 — Test Connection (`ping`)

Verify that your API keys work and the Binance Testnet is reachable:

```bash
python cli.py ping
```

**What you'll see on success:**
```
>>> Checking connectivity to Binance Futures Testnet...
╭─ Status Online ──────────────────────────╮
│  [OK] Connection test succeeded!         │
│  Binance Futures Testnet is reachable.   │
╰──────────────────────────────────────────╯
```

**What you'll see on failure:**
- If API keys are missing → a red panel tells you to configure `.env`
- If the network is down → an error panel with the connection details

---

### Command 2 — Place an Order (`order`)

The `order` command accepts these flags:

| Flag | Short | Required | Description |
|---|---|---|---|
| `--symbol` | `-s` | ✅ | Trading pair: `BTCUSDT`, `ETHUSDT`, or `BNBUSDT` |
| `--side` | `-d` | ✅ | Direction: `BUY` or `SELL` |
| `--type` | `-t` | ✅ | Order type: `MARKET`, `LIMIT`, or `STOP_MARKET` |
| `--quantity` | `-q` | ✅ | Amount to trade (e.g. `0.001`) |
| `--price` | `-p` | ❌ | Required for `LIMIT` and `STOP_MARKET` only |

---

### CLI Examples

**Buy 0.001 BTC at Market Price:**
```bash
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

**Sell 0.01 ETH with a Limit Order at $3,200:**
```bash
python cli.py order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 3200
```

**Place a Stop-Market (Stop-Loss) Trigger at $58,000 for BTC:**
```bash
python cli.py order --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --price 58000
```

> 📝 **Note:** Stop-Market orders use the Binance Algo Order Service (`/fapi/v1/algoOrder`) under the hood, as required by the December 2025 Binance API migration.

**Short-form using flag aliases:**
```bash
python cli.py order -s BTCUSDT -d BUY -t MARKET -q 0.005
```

After a successful order, you'll see a styled **Execution Receipt** panel in your terminal showing the Order ID, Status (FILLED/NEW), Side, Type, and more.

---

## 📋 Logging

The bot automatically writes detailed logs to the `logs/` directory:

| Log File | Level | What It Records |
|---|---|---|
| `logs/trading.log` | DEBUG+ | Every API request/response, parameter validation, order flow |
| `logs/errors.log` | ERROR+ | HTTP failures, connection timeouts, exchange rejections |

You can open these files in any text editor to review historical activity.

---

## ❓ Troubleshooting

| Problem | Solution |
|---|---|
| **"API Credentials Missing"** error | Make sure `.env` exists in the project root and contains your actual API Key and Secret (not the placeholder values) |
| **"Connection test failed"** | Check your internet connection. The Binance Testnet may also be temporarily down — try again in a few minutes |
| **"Insufficient margin"** or HTTP 400 errors | Your testnet account needs funds. Go to [testnet.binancefuture.com](https://testnet.binancefuture.com) and click the **Faucet** button to get free test USDT |
| **Order rejected with "Invalid quantity"** | Each symbol has minimum quantity rules. Try larger amounts (e.g. `0.001` for BTC, `0.01` for ETH, `0.1` for BNB) |
| **GUI page doesn't load** | Make sure `python gui.py` is still running in your terminal. Check for error messages. Try visiting `http://127.0.0.1:5000` manually |
| **Positions not updating** | Click the 🔄 sync button or wait 10 seconds for the auto-refresh cycle |
| **Browser didn't auto-open** | Manually navigate to `http://127.0.0.1:5000` in Chrome, Firefox, Edge, or any browser |
| **"ModuleNotFoundError"** | Make sure your virtual environment is activated (you should see `(.venv)` in your terminal prompt) and run `pip install -r requirements.txt` again |

---

## 🔒 Security

- Your API keys are stored locally in `.env` which is **git-ignored** and **never** pushed to GitHub
- The bot runs entirely on your local machine — no data is sent to any third-party server
- All communication is directly between your machine and the official Binance Futures Testnet API (`https://testnet.binancefuture.com`)
- Requests are signed using HMAC-SHA256 per Binance's authentication specification

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.10+ |
| Web Framework | Flask 3.0+ |
| CLI Framework | Typer 0.9+ with Rich 13.7+ |
| API Client | Requests with HMAC-SHA256 signing |
| Environment | python-dotenv |
| Frontend | Vanilla HTML/CSS/JS with Outfit + JetBrains Mono fonts |
| Theme | Custom HSL navy-dark fintech palette |

---

## 📝 License

This project is for **educational and testing purposes only** using the Binance Futures Testnet. Do not use real API keys or real funds with this bot.
