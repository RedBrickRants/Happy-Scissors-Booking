# appointments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Appointment CRUD
    path('', views.appointment_list, name='appointment-list'),
    path('create/', views.create_appointment, name='create-appointment'),
    path('<int:appointment_id>/', views.appointment_detail, name='appointment-detail'),
    path('<int:appointment_id>/status/', views.update_appointment_status, name='update-appointment-status'),
    
    # Appointment queries
    path('today/', views.today_appointments, name='today-appointments'),
    path('upcoming/', views.upcoming_appointments, name='upcoming-appointments'),
]