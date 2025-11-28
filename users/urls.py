from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

# url patterns are meant to route requests to the appropriate views s
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('client-profile/', views.client_profile, name='client-profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('test/', views.simple_test, name='simple-test'),
]