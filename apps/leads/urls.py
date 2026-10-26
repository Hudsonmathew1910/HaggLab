from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.start_project_view, name='start_project'),
    path('thank-you/', views.thank_you_view, name='thank_you'),
]
