import pandas as pd

def add_indicators(df_prices):
    df = df_prices.copy()
    df['price'] = df['price'].astype(float)

    df = df.sort_values('date')
    df['daily_return'] = df['price'].pct_change()
    df['ma_7'] = df['price'].rolling(window=7).mean()
    df['ma_30'] = df['price'].rolling(window=30).mean()
    df['volatility'] = df['daily_return'].rolling(window=30).std()

    return df[['date', 'daily_return', 'ma_7', 'ma_30', 'volatility']]
