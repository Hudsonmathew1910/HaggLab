from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('clear/', views.clear_chat_view, name='clear_chat'),
    path('api/search/', views.search_api_view, name='api_search'),
    path('health/', views.health_view, name='health'),
]
