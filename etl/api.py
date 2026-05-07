import time
import logging
import requests
import pandas as pd

def fetch_with_retry(url, params=None, max_retries=5):
    delay = 2 #seconds

    for attempt in range(max_retries):
        resp = requests.get(url, params=params)

        # Rate limit
        if resp.status_code == 429:
            logging.warning(f'Rate limit hit. Waiting {delay} seconds...')
            time.sleep(delay)
            delay *= 2
            continue

        resp.raise_for_status()
        logging.info('API call succeeded')
        return resp.json()
    
    logging.error('API failed after retries')
    raise Exception('API failed after retries')

def fetch_market_chart(coin_id, full_history=False):
    url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart'
    
    # Only fetch 2 days for incremental loads
    params = {
        'vs_currency': 'usd',
        'days': '365' if full_history else '2' 
    }

    return fetch_with_retry(url, params=params)

def parse_market_chart(data):
    prices = data.get('prices', [])
    market_caps = data.get('market_caps', [])
    volumes = data.get('total_volumes', [])

    df_price = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df_mcap = pd.DataFrame(market_caps, columns=['timestamp', 'market_cap'])
    df_vol = pd.DataFrame(volumes, columns=['timestamp', 'volume'])

    df = df_price.merge(df_mcap, on='timestamp').merge(df_vol, on='timestamp')
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.date.astype(str)
    return df[['date', 'price', 'market_cap', 'volume']]