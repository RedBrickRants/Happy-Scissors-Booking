# staff/urls.py
from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    # Staff CRUD
    path('', views.staff_list, name='staff-list'),
    path('create/', views.staff_create, name='staff-create'),
    path('<int:staff_id>/', views.staff_detail, name='staff-detail'),
    path('<int:staff_id>/toggle-active/', views.staff_toggle_active, name='staff-toggle-active'),
    
    # Staff scheduling
    path('<int:staff_id>/availability/', views.staff_availability, name='staff-availability'),
    path('<int:staff_id>/schedule/', views.staff_schedule, name='staff-schedule'),
]