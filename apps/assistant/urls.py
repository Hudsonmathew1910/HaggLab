from django.urls import path

from . import views

urlpatterns = [
    path('api/assistant/', views.assistant_api, name='assistant_api'),
]
