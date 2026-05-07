CREATE TABLE IF NOT EXISTS dim_asset (
    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,
    name TEXT,
);

CREATE TABLE IF NOT EXISTS fact_price_history (
    asset_id INTEGER,
    date TEXT,
    price REAL,
    market_cap REAL,
    volume REAL
);

CREATE TABLE IF NOT EXISTS fact_indicators (
    asset_id INTEGER,
    date TEXT,
    daily_return REAL,
    ma_7 REAL,
    ma_30 REAL,
    volatility REAL
);