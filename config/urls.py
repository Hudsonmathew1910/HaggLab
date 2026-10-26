from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls import handler404, handler500

urlpatterns = [
    path(settings.ADMIN_URL_PATH, admin.site.urls),
    path('', include('apps.analytics.urls')),
    path('', include('apps.leads.urls')),
    path('', include('apps.tryit.urls')),
    path('', include('apps.core.urls')),
]



handler404 = 'apps.core.views.custom_404_view'
handler500 = 'apps.core.views.custom_500_view'
