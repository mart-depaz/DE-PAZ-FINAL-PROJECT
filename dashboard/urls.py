# for dashboard app
# dashboard/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard-dashboard'),
    path('dashboard/official/', views.official_dashboard, name='dashboard-official'),
    path('dashboard/member/', views.member_dashboard, name='dashboard-member'),
    path('profile/', views.profile, name='profile'),
    path('notifications/', views.notifications, name='notifications'),
    path('population/', views.population, name='population'),
    path('about/', views.about, name='about'),
]