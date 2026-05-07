CREATE VIEW IF NOT EXISTS vw_price_with_indicators AS
SELECT
    p.asset_id,
    p.date,
    p.price,
    p.market_cap,
    p.volume,
    i.daily_return,
    i.ma_7,
    i.ma_30,
    i.volatility
FROM fact_price_history p
LEFT JOIN fact_indicators i
    ON p.asset_id = i.asset_id
    AND p.date = i.date;

CREATE VIEW IF NOT EXISTS vw_latest_price AS
SELECT
    asset_id,
    MAX(date) AS latest_date,
    price
FROM fact_price_history
GROUP BY asset_id;