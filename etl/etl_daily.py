import logging
import pandas as pd

from api import fetch_market_chart, parse_market_chart
from db import (
    init_db, get_connection, upsert_assets, clean_dim_asset, get_latest_date, delete_overlap_rows, load_data
)
from indicators import add_indicators
from utils import get_overlap_start, setup_logger

COINS = {
    'bitcoin': 'BTC',
    'ethereum': 'ETH',
    'solana': 'SOL',
    'binancecoin': 'BNB',
    'ripple': 'XRP'
}

def run_etl():
    setup_logger()
    logging.info('Starting ETL pipeline')

    init_db()
    conn = get_connection()
    upsert_assets(conn)
    clean_dim_asset(conn)

    for coin_id, symbol in COINS.items():
        logging.info(f'Processing {symbol}...')

        cur = conn.cursor()
        cur.execute('SELECT asset_id FROM dim_asset WHERE symbol = %s', (symbol,))
        asset_id = cur.fetchone()[0]

        latest_date = get_latest_date(conn, asset_id)

        full_history = latest_date is None

        if full_history:
            logging.info(' First run -> loading full history')
        else:
            logging.info(f' Latest date in DB: {latest_date}')

        start_date = get_overlap_start(latest_date, days_overlap=1)
        logging.info(f' Reloading from {start_date}')

        raw = fetch_market_chart(coin_id, full_history=full_history)
        df_full = parse_market_chart(raw)
        df_new = df_full[df_full['date'] >= start_date]

        if df_new.empty:
            logging.info(f' No new data for {symbol}')
            continue

        delete_overlap_rows(conn, asset_id, start_date)

        df_indicators = add_indicators(df_new)
        load_data(conn, asset_id, df_new, df_indicators)

        logging.info(f' Inserted {len(df_new)} rows for {symbol}')

    conn.close()
    logging.info('ETL completed successfully.')

if __name__ == '__main__':
    run_etl()