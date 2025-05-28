import json
import yfinance as yf
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Trade, PortfolioEntry

def portfolio_list(request):
    entries = PortfolioEntry.objects.all().values(
        'symbol', 'shares', 'average_price'
    )
    return JsonResponse(list(entries), safe=False)

@csrf_exempt
def trades_post(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Only POST method allowed.")

    try:
        data = json.loads(request.body)
        symbol = data['symbol'].upper()
        action = data['action'].upper()
        shares = int(data['shares'])

        if action not in ['BUY', 'SELL']:
            return HttpResponseBadRequest("Action must be BUY or SELL.")

        # Get current price from yfinance
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        if hist.empty:
            return HttpResponseBadRequest(f"No data found for {symbol}")
        price = hist['Close'].iloc[-1]

        # ✅ Validate first before logging the trade
        if action == 'BUY':
            try:
                entry = PortfolioEntry.objects.get(symbol=symbol)
                total_shares = entry.shares + shares
                total_cost = (entry.shares * entry.average_price) + (shares * price)
                new_avg_price = total_cost / total_shares

                entry.shares = total_shares
                entry.average_price = new_avg_price
                entry.save()
            except PortfolioEntry.DoesNotExist:
                PortfolioEntry.objects.create(
                    symbol=symbol,
                    shares=shares,
                    average_price=price
                )

        elif action == 'SELL':
            try:
                entry = PortfolioEntry.objects.get(symbol=symbol)
                if entry.shares < shares:
                    return HttpResponseBadRequest("Not enough shares to sell.")
                entry.shares -= shares
                if entry.shares == 0:
                    entry.delete()
                else:
                    entry.save()
            except PortfolioEntry.DoesNotExist:
                return HttpResponseBadRequest("You do not own this stock.")

        # ✅ Log the trade only after successful portfolio update
        Trade.objects.create(
            symbol=symbol,
            action=action,
            shares=shares,
            price=price
        )

        return JsonResponse({
            'message': f'{action} {shares} shares of {symbol} @ ${price:.2f}',
            'symbol': symbol,
            'shares': shares,
            'price': round(price, 2)
        }, status=201)

    except (KeyError, ValueError):
        return HttpResponseBadRequest("Invalid request data.")

def get_trades(request):
    symbol = request.GET.get('symbol')
    trades = Trade.objects.all().order_by('-timestamp')

    if symbol:
        trades = trades.filter(symbol=symbol.upper())

    data = list(trades.values(
        'symbol',
        'action',
        'shares',
        'price',
        'timestamp'
    ))

    return JsonResponse(data, safe=False)
