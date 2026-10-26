from django.urls import path

from . import views

urlpatterns = [
    path('projects/<slug:slug>/try/', views.try_view, name='try_project'),
    path('api/try/<slug:slug>/', views.try_api, name='try_api'),
]
