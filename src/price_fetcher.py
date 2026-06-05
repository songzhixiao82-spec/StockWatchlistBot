import yfinance as yf


def get_latest_price(ticker: str) -> float | None:
    ticker = ticker.upper()

    if ticker == "CASH":
        return 1.0

    try:
        stock = yf.Ticker(ticker)

        # First try fast_info
        try:
            price = stock.fast_info.get("last_price")
            if price is not None:
                return float(price)
        except Exception:
            pass

        # Fallback to latest 1-minute close
        hist = stock.history(period="1d", interval="1m")
        if not hist.empty:
            return float(hist["Close"].dropna().iloc[-1])

        # Final fallback to daily close
        hist = stock.history(period="5d", interval="1d")
        if not hist.empty:
            return float(hist["Close"].dropna().iloc[-1])

        return None

    except Exception as e:
        print(f"[WARN] Failed to fetch price for {ticker}: {e}")
        return None
