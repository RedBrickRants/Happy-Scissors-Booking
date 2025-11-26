from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def appointment_list(request):
    return Response({'message': 'Appointment list endpoint'})

@api_view(['POST'])
def create_appointment(request):
    return Response({'message': 'Create appointment endpoint'})