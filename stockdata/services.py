import yfinance as yf

def get_current_price(symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1d")
    if hist.empty:
        return None
    return hist['Close'].iloc[-1]
