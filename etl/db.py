import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS dim_asset (
            asset_id SERIAL PRIMARY KEY,
            symbol TEXT UNIQUE,
            name TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS fact_price_history (
            asset_id INTEGER REFERENCES dim_asset(asset_id),
            date DATE,
            price DOUBLE PRECISION,
            market_cap DOUBLE PRECISION,
            volume DOUBLE PRECISION,
            PRIMARY KEY (asset_id, date)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS fact_indicators (
            asset_id INTEGER REFERENCES dim_asset(asset_id),
            date DATE,
            daily_return DOUBLE PRECISION,
            ma_7 DOUBLE PRECISION,
            ma_30 DOUBLE PRECISION,
            volatility DOUBLE PRECISION,
            PRIMARY KEY (asset_id, date)
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
        cur.execute('''
            INSERT INTO dim_asset (symbol, name)
            VALUES (%s, %s)
            ON CONFLICT (symbol) DO UPDATE
            SET name = EXCLUDED.name;
        ''', (symbol, name.lower()))

    conn.commit()

def clean_dim_asset(conn):
    cur = conn.cursor()
    cur.execute('''
        DELETE FROM dim_asset
        WHERE asset_id NOT IN (
            SELECT MIN(asset_id)
            FROM dim_asset
            GROUP BY symbol
        )
    ''')
    conn.commit()

def get_latest_date(conn, asset_id):
    cur = conn.cursor()
    cur.execute('SELECT MAX(date) FROM fact_price_history WHERE asset_id = %s', (asset_id,))
    row = cur.fetchone()
    return row[0].strftime('%Y-%m-%d') if row and row[0] else None 

def delete_overlap_rows(conn, asset_id, start_date):
    cur = conn.cursor()
    cur.execute('DELETE FROM fact_price_history WHERE asset_id = %s AND date >= %s', (asset_id, start_date))
    cur.execute('DELETE FROM fact_indicators WHERE asset_id = %s AND date >= %s', (asset_id, start_date))
    conn.commit()

def load_data(conn, asset_id, df_price, df_indicators):
    cur = conn.cursor()

    price_rows = [
        (asset_id, row['date'], float(row['price']), float(row['market_cap']), float(row['volume']))
        for _, row in df_price.iterrows()
    ]
    cur.executemany('''
        INSERT INTO fact_price_history (asset_id, date, price, market_cap, volume)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (asset_id, date) DO UPDATE
        SET price = EXCLUDED.price,
            market_cap = EXCLUDED.market_cap,
            volume = EXCLUDED.volume
    ''', price_rows)

    indicator_rows = [
        (
            asset_id, row['date'], 
            None if pd.isna(row['daily_return']) else float(row['daily_return']),
            None if pd.isna(row['ma_7']) else float(row['ma_7']),
            None if pd.isna(row['ma_30']) else float(row['ma_30']),
            None if pd.isna(row['volatility']) else float(row['volatility'])
        )
        for _, row in df_indicators.iterrows()
    ]
    cur.executemany('''
        INSERT INTO fact_indicators (asset_id, date, daily_return, ma_7, ma_30, volatility)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (asset_id, date) DO UPDATE
        SET daily_return = EXCLUDED.daily_return,
            ma_7 = EXCLUDED.ma_7,
            ma_30 = EXCLUDED.ma_30,
            volatility = EXCLUDED.volatility
    ''', indicator_rows)

    conn.commit()