from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('solutions/', views.solutions_hub_view, name='solutions_hub'),
    path('solutions/<slug:slug>/', views.solution_detail_view, name='solution_detail'),
    path('projects/', views.projects_hub_view, name='projects_hub'),
    path('projects/<slug:slug>/', views.project_detail_view, name='project_detail'),
    path('process/', views.process_view, name='process'),
    path('security/', views.security_view, name='security_data'),
    path('about/', views.about_view, name='about'),
    path('faq/', views.faq_view, name='faq'),
    path('hire/', views.hire_fiverr_view, name='hire_fiverr'),
    path('privacy/', views.privacy_view, name='privacy_policy'),
    path('terms/', views.terms_view, name='terms_of_service'),
    path('styleguide/', views.styleguide_view, name='styleguide'),
    path('health/', views.health_check, name='health_check'),
    path('robots.txt', views.robots_txt_view, name='robots'),
    path('sitemap.xml', views.sitemap_xml_view, name='sitemap'),
]
