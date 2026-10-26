from django.urls import path
from . import views

urlpatterns = [
    path('api/analytics/event/', views.record_event_view, name='analytics_event'),
]
