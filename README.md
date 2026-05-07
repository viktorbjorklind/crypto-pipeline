# Crypto ETL Pipeline (Incremental + Indicators)

A modular, production-style ETL pipeline that:

- Fetches historical crypto data from CoinGecko
- Loads into a SQLite database
- Computes technical indicators (MA7, MA30, volatility)
- Supports incremental loading with overlap correction
- Uses clean, maintainable architecture

## Project Structure
etl/
etl_daily.py
api.py
db.py
indicators.py
utils.py
data/
logs/

## How to Run
python etl/etl_daily.py

## Features

- Incremental loading
- 1-day overlap to correct revised API data
- Modular design
- SQLite storage
- Technical indicators