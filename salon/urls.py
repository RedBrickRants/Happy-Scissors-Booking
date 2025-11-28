from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/appointments/', include('appointments.urls')),
    path('api/services/', include('services.urls')),
    path('api/clients/', include('clients.urls')),
    path('api/business/', include('business.urls')),
    path('api/staff/', include('staff.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/reports/', include('reports.urls')),
    
]