from django.urls import path
from . import views

app_name = 'flight_deals'
urlpatterns = [
    path('', views.flight_deals_home, name='home'),
    path('api/refresh/', views.refresh_deals_api, name='refresh'),
]