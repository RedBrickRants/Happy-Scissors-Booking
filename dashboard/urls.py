# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_overview, name='dashboard-overview'),
    path('stats/', views.dashboard_stats, name='dashboard-stats'),
    path('calendar/', views.calendar_view, name='calendar-view'),
    path('staff-performance/', views.staff_performance, name='staff-performance'),
]