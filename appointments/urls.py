from django.urls import path
from . import views

urlpatterns = [
    path('', views.appointment_list, name='appointment-list'),
    path('create/', views.create_appointment, name='create-appointment'),
]