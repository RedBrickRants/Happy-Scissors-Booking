from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from .models import CustomUser

@api_view(['POST'])
def register(request):
    # Basic registration view - we'll expand this later
    return Response({'message': 'Registration endpoint'})

@api_view(['POST'])
def login(request):
    # Basic login view - we'll expand this later
    return Response({'message': 'Login endpoint'})