import requests
import pandas as pd
import sqlite3
from datetime import datetime
from indicators import add_indicators

DB_PATH = 'data/crypto.db'

COINS = {
    'bitcoin': 'BTC',
    'ethereum': 'ETH',
    'solana': 'SOL',
    'binancecoin': 'BNB',
    'ripple': 'XRP'
}

def fetch_market_data(coin_id):
    url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart'
    params = {'vs_currency': 'usd', 'days': '365'}
    r = requests.get(url, params=params)
    data = r.json()
    
    # Handle API errors
    if 'prices' not in data or not data['prices']:
        print(f'API returned no data for {coin_id}: {data}')
        return pd.DataFrame()

    prices = data.get('prices', [])
    market_caps = data.get('market_caps', [])
    volumes = data.get('total_volumes', [])

    df = pd.DataFrame(prices, columns=['timestamp', 'price'])

    df['market_cap'] = [mc[1] for mc in market_caps] if market_caps else None
    df['volume'] = [v[1] for v in volumes] if volumes else None

    df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.date
    df = df[['date', 'price', 'market_cap', 'volume']]

    return df

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS dim_asset (
            asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
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

def get_asset_id(symbol, name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute('SELECT asset_id FROM dim_asset WHERE symbol = ?', (symbol,))
    row = cur.fetchone()

    if row:
        conn.close()
        return row[0]
    
    cur.execute('INSERT INTO dim_asset (symbol, name) VALUES (?, ?)', (symbol, name))
    conn.commit()
    asset_id = cur.lastrowid
    conn.close()
    return asset_id

def load_data(asset_id, df_prices, df_indicators):
    conn = sqlite3.connect(DB_PATH)

    df_prices['asset_id'] = asset_id
    df_indicators['asset_id'] = asset_id

    # DEBUG CHECK - see what columns are being inserted
    #print('INDICATOR COLUMNS:', df_indicators.columns.tolist())
    #print(df_indicators.head())

    df_prices.to_sql('fact_price_history', conn, if_exists='append', index=False)
    df_indicators.to_sql('fact_indicators', conn, if_exists='append', index=False)

    conn.close()

def run_etl():
    init_db()

    for coin_id, symbol in COINS.items():
        print(f'Processing {symbol}...')

        df = fetch_market_data(coin_id)
        if df.empty:
            print(f'Skipping {symbol}, no data returned.')
            continue

        df_ind = add_indicators(df.copy())

        asset_id = get_asset_id(symbol, coin_id.capitalize())
        load_data(asset_id, df, df_ind)

    print('ETL completed successfully.')

if __name__ == '__main__':
    run_etl()