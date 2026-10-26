from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('api/query/', views.query_api_view, name='api_query'),
    path('health/', views.health_view, name='health'),
]
