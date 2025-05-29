from django.urls import path
from .views import RegisterUser, CustomAuthToken, logout_view

urlpatterns = [
path('register/', RegisterUser.as_view(), name='register'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
]
