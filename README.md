# Crypto ETL Pipeline

A modular, production-style ETL pipeline that fetches historical crypto data from CoinGecko, computes technical indicators, and loads everything into a PostgreSQL database. Supports incremental loading with overlap correction.

## Project Structure

CRYPTO-PIPELINE/
├── etl/
│   ├── api.py           # CoinGecko API calls and parsing
│   ├── db.py            # PostgreSQL connection and data loading
│   ├── etl_daily.py     # Main pipeline entry point
│   ├── indicators.py    # Technical indicator calculations
│   └── utils.py         # Logging and date helpers
├── logs/                # Auto-generated on first run
├── powerbi/
│   └── crypto_etl.pbix
├── .env                 # Local secrets, not committed
├── .gitignore
├── README.md
└── requirements.txt

## Setup

1. Install dependencies:
   pip install -r requirements.txt

2. Create a .env file in the root:
   DB_HOST=localhost
   DB_NAME=crypto_etl
   DB_USER=postgres
   DB_PASSWORD=your_password

3. Run the pipeline:
   python etl/etl_daily.py

## Features

- Incremental loading with 1-day overlap to correct revised API data
- Full history load on first run, daily updates thereafter
- Technical indicators: daily return, MA7, MA30, volatility
- PostgreSQL storage with upsert logic
- Rotating log files under logs/

## Coins Tracked

Bitcoin, Ethereum, Solana, BNB, XRP