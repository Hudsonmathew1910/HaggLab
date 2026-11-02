from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.start_project_view, name='start_project'),
    path('thank-you/', views.thank_you_view, name='thank_you'),
    path('staff/inquiry-file/<int:pk>/', views.inquiry_file_view, name='inquiry_file'),
]
