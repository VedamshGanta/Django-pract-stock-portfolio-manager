import yfinance as yf
from django.http import JsonResponse
import numpy as np

def current_price(request, symbol):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d")
    price = data['Close'].iloc[-1]
    return JsonResponse({'symbol': symbol, 'current_price': price})

def history(request, symbol):
    period = request.GET.get('period', '7d')
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period).reset_index()
    data = df[['Date', 'Close']].to_dict(orient='records')
    return JsonResponse({'symbol': symbol, 'history': data})

def summary_stats(request, symbol):
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="30d")
    closes = df['Close'].values
    avg = np.mean(closes)
    std = np.std(closes)
    return JsonResponse({
        'symbol': symbol,
        'average_price': round(avg, 2),
        'volatility': round(std, 2)
    })
