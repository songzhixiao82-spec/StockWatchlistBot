from datetime import datetime, timedelta
import pandas as pd

from src.config import WATCHLIST_PATH, ALERT_LOG_PATH
from src.price_fetcher import get_latest_price
from src.email_sender import send_email


def load_watchlist() -> pd.DataFrame:
    return pd.read_csv(WATCHLIST_PATH)


def load_alert_log() -> pd.DataFrame:
    try:
        return pd.read_csv(ALERT_LOG_PATH)
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            'timestamp',
            'ticker',
            'alert_type',
            'price',
            'message'
        ])


def save_alert_log(alert_log: pd.DataFrame) -> None:
    alert_log.to_csv(ALERT_LOG_PATH, index=False)


def was_recently_alerted(
    alert_log: pd.DataFrame,
    ticker: str,
    alert_type: str,
    cooldown_hours: int,
) -> bool:
    if alert_log.empty:
        return False

    rows = alert_log[
        (alert_log['ticker'].str.upper() == ticker.upper())
        & (alert_log['alert_type'] == alert_type)
    ]

    if rows.empty:
        return False

    last_time = pd.to_datetime(rows['timestamp']).max()
    return datetime.now() - last_time < timedelta(hours=cooldown_hours)


def build_buy_email(
    ticker: str,
    name: str,
    price: float,
    buy_low: float,
    buy_high: float,
    thesis: str,
    priority: str,
) -> tuple[str, str]:
    subject = f'[STOCK BUY ALERT] {ticker} entered buy zone'

    body = f'''
{ticker} - {name}

Current price: ${price:.2f}
Buy zone: ${buy_low:.2f} - ${buy_high:.2f}
Priority: {priority}

Action:
Price entered your actionable buy zone. Review and decide whether to buy.

Thesis:
{thesis}

Reminder:
This is an alert, not an auto-trade. Check current market context before placing an order.
'''.strip()

    return subject, body


def build_sell_email(
    ticker: str,
    name: str,
    price: float,
    sell_low: float,
    sell_high: float,
    thesis: str,
    priority: str,
) -> tuple[str, str]:
    subject = f'[STOCK SELL/TRIM ALERT] {ticker} entered sell zone'

    body = f'''
{ticker} - {name}

Current price: ${price:.2f}
Sell / trim zone: ${sell_low:.2f} - ${sell_high:.2f}
Priority: {priority}

Action:
Price entered your sell / trim review zone. Review whether to trim, sell, or keep holding.

Thesis:
{thesis}
'''.strip()

    return subject, body


def run_alert_check() -> None:
    watchlist = load_watchlist()
    alert_log = load_alert_log()
    new_alerts = []

    print('=' * 80)
    print('Running stock price alert check')
    print('=' * 80)

    for _, row in watchlist.iterrows():
        ticker = str(row['ticker']).upper()
        name = str(row['name'])
        action = str(row['action']).lower()
        status = str(row['status']).lower()
        priority = str(row['priority'])
        cooldown_hours = int(row['cooldown_hours'])
        thesis = str(row['thesis'])

        if status != 'active':
            continue

        price = get_latest_price(ticker)

        if price is None:
            print(f'[SKIP] {ticker}: no price found')
            continue

        buy_low = float(row['buy_low'])
        buy_high = float(row['buy_high'])
        sell_low = float(row['sell_low'])
        sell_high = float(row['sell_high'])

        print(f'{ticker}: ${price:.2f}')

        if action in ['buy', 'buy_or_sell']:
            if buy_low > 0 and buy_high > 0 and buy_low <= price <= buy_high:
                alert_type = 'buy_zone'

                if not was_recently_alerted(alert_log, ticker, alert_type, cooldown_hours):
                    subject, body = build_buy_email(
                        ticker=ticker,
                        name=name,
                        price=price,
                        buy_low=buy_low,
                        buy_high=buy_high,
                        thesis=thesis,
                        priority=priority,
                    )
                    send_email(subject, body)

                    new_alerts.append({
                        'timestamp': datetime.now().isoformat(timespec='seconds'),
                        'ticker': ticker,
                        'alert_type': alert_type,
                        'price': price,
                        'message': subject,
                    })

        if action in ['sell', 'buy_or_sell']:
            if sell_low > 0 and sell_high > 0 and sell_low <= price <= sell_high:
                alert_type = 'sell_zone'

                if not was_recently_alerted(alert_log, ticker, alert_type, cooldown_hours):
                    subject, body = build_sell_email(
                        ticker=ticker,
                        name=name,
                        price=price,
                        sell_low=sell_low,
                        sell_high=sell_high,
                        thesis=thesis,
                        priority=priority,
                    )
                    send_email(subject, body)

                    new_alerts.append({
                        'timestamp': datetime.now().isoformat(timespec='seconds'),
                        'ticker': ticker,
                        'alert_type': alert_type,
                        'price': price,
                        'message': subject,
                    })

    if new_alerts:
        alert_log = pd.concat([alert_log, pd.DataFrame(new_alerts)], ignore_index=True)
        save_alert_log(alert_log)
        print(f'[DONE] {len(new_alerts)} new alerts sent.')
    else:
        print('[DONE] No new alerts.')
