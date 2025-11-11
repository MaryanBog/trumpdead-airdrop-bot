# 🪙 TRUMPDEAD Airdrop Bot

A fully automated airdrop bot for the **Solana** blockchain that sends SPL tokens to users directly through Telegram.

---

## ⚙️ Tech Stack

- **Python 3.10+**
- **FastAPI + Uvicorn** — HTTP API service
- **python-telegram-bot** — Telegram integration
- **solders / solana-py** — Solana blockchain SDK
- **Railway** — hosting for both Web (API) and Worker (Bot)

---

## 🧩 Architecture Overview

- **`web`** — FastAPI service (`core_service.py`)  
  Handles POST `/airdrop`, builds and sends transactions via Solana RPC.  
  Automatically creates Associated Token Accounts (ATA) for new recipients.

- **`worker`** — Telegram bot (`main.py`)  
  Accepts commands like `/start` and `/airdrop <wallet>`,  
  and communicates with the Web API.

---

## 🔐 Environment Variables (`.env`)

| Variable | Description |
|-----------|--------------|
| `BOT_TOKEN` | Telegram bot token from **@BotFather** |
| `PRIVATE_KEY` | Base58 private key of the Solana wallet used for sending |
| `RPC_URL` | Solana RPC endpoint (`https://api.mainnet-beta.solana.com` or `https://api.devnet.solana.com`) |
| `AIRDROP_AMOUNT` | Amount of tokens to send per airdrop |
| `MINT_ADDRESS` | SPL token mint address (`Pubkey`) |
| `CHANNEL_USERNAME` | Telegram channel name for subscription check |
| `PYTHONUNBUFFERED` | 1 (enables unbuffered logging) |

---

## 🚀 Deployment on Railway

### 1. Connect GitHub Repository
Import the project into [Railway.app](https://railway.app).  
It will automatically create two services:
- **web** (FastAPI)
- **worker** (Telegram Bot)

### 2. Set Environment Variables
Add all variables either via **Railway → Variables**  
or by uploading your `.env` file.

Make sure `PRIVATE_KEY` and `BOT_TOKEN` are correct.

### 3. Verify `Procfile`
