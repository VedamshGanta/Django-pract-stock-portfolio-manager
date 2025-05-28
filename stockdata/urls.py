from django.urls import path
from . import views

urlpatterns = [
    path('<str:symbol>/price/', views.current_price, name='current-price'),
    path('<str:symbol>/history/', views.history, name='stock-history'),
    path('<str:symbol>/summary/', views.summary_stats, name='stock-summary'),
]
