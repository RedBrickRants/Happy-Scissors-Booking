from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def business_settings(request):
    """Business configuration"""
    if not request.user.is_admin_user():
        return Response({'error': 'Admin access required'}, status=403)
    return Response({"message": "Business settings endpoint"})