import sqlite3
import os

DB_PATH = os.path.join('data', 'crypto.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS dim_asset (
            asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE,
            name TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS fact_price_history (
            asset_id INTEGER,
            date TEXT,
            price REAL,
            market_cap REAL,
            volume REAL
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS fact_indicators (
            asset_id INTEGER,
            date TEXT,
            daily_return REAL,
            ma_7 REAL,
            ma_30 REAL,
            volatility REAL
        )
    ''')

    conn.commit()
    conn.close()

def upsert_assets(conn):
    cur = conn.cursor()
    assets = {
        'bitcoin': 'BTC',
        'ethereum': 'ETH',
        'solana': 'SOL',
        'binancecoin': 'BNB',
        'ripple': 'XRP'
    }
    for name, symbol in assets.items():
        cur.execute('INSERT OR IGNORE INTO dim_asset (symbol, name) VALUES (?, ?)', (symbol, name.lower()))
    conn.commit()

def clean_dim_asset(conn):
    '''
    Removes duplicate rows from dim_asset, keeping only one per symbol.
    '''
    cur = conn.cursor()
    cur.execute('''
        DELETE FROM dim_asset
        WHERE rowid NOT IN (
            SELECT MIN(rowid)
            FROM dim_asset
            GROUP BY symbol
        )
    ''')
    conn.commit()

def get_latest_date(conn, asset_id):
    cur = conn.cursor()
    cur.execute('SELECT MAX(date) FROM fact_price_history WHERE asset_id = ?', (asset_id,))
    return cur.fetchone()[0]

def delete_overlap_rows(conn, asset_id, start_date):
    cur = conn.cursor()
    cur.execute('DELETE FROM fact_price_history WHERE asset_id = ? AND date >= ?', (asset_id, start_date))
    cur.execute('DELETE FROM fact_indicators WHERE asset_id = ? AND date >= ?', (asset_id, start_date))
    conn.commit()

def load_data(conn, asset_id, df_prices, df_indicators):
    df_prices = df_prices.copy()
    df_indicators = df_indicators.copy()

    df_prices['asset_id'] = asset_id
    df_indicators['asset_id'] = asset_id

    df_prices.to_sql('fact_price_history', conn, if_exists='append', index=False)
    df_indicators.to_sql('fact_indicators', conn, if_exists='append', index=False)