import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Trade, PortfolioEntry
from stockdata.services import get_current_price
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def portfolio_list(request):
    entries = PortfolioEntry.objects.filter(user=request.user).values(
        'symbol', 'shares', 'average_price'
    )
    return JsonResponse(list(entries), safe=False)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def trades_post(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Only POST method allowed.", status=400)

    try:
        data = json.loads(request.body)
        symbol = data['symbol'].upper()
        action = data['action'].upper()
        shares = int(data['shares'])

        if action not in ['BUY', 'SELL']:
            return HttpResponseBadRequest("Action must be BUY or SELL.", status=400)


        price = get_current_price(symbol)
        if price is None:
            return HttpResponseBadRequest(f"No data found for {symbol}", status=404)

        # Validate first before logging the trade
        if action == 'BUY':
            try:
                entry = PortfolioEntry.objects.get(user=request.user, symbol=symbol)
                total_shares = entry.shares + shares
                total_cost = (entry.shares * entry.average_price) + (shares * price)
                new_avg_price = total_cost / total_shares

                entry.shares = total_shares
                entry.average_price = new_avg_price
                entry.save()
            except PortfolioEntry.DoesNotExist:
                PortfolioEntry.objects.create(
                    user=request.user,
                    symbol=symbol,
                    shares=shares,
                    average_price=price
                )

        elif action == 'SELL':
            try:
                entry = PortfolioEntry.objects.get(user=request.user, symbol=symbol)
                if entry.shares < shares:
                    return HttpResponseBadRequest("Not enough shares to sell.", status=403)
                entry.shares -= shares
                if entry.shares == 0:
                    entry.delete()
                else:
                    entry.save()
            except PortfolioEntry.DoesNotExist:
                return HttpResponseBadRequest("You do not own this stock.", status=404)

        Trade.objects.create(
            user=request.user,
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

    except KeyError as e:
        return HttpResponseBadRequest(f"Missing field: {str(e)}", status=400)
    except ValueError:
        return HttpResponseBadRequest("Invalid data type for 'shares'. Must be an integer.", status=400)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_trades(request):
    symbol = request.GET.get('symbol')
    trades = Trade.objects.filter(user=request.user).order_by('-timestamp')

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
