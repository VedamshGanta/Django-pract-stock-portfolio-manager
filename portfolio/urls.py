from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio_list, name='portfolio-list'),
    path('trades/', views.trades_post, name='trades-post'),
    path('trades/history/', views.get_trades, name='trades-get'),
]
