from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Service
from .serializers import ServiceSerializer

@api_view(['GET'])
def service_list(request):
    services = Service.objects.filter(active=True)
    serializer = ServiceSerializer(services, many=True)
    return Response(serializer.data)