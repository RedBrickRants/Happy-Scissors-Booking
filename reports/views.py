from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reports_overview(request):
    """Reports overview"""
    if not request.user.is_admin_user():
        return Response({'error': 'Admin access required'}, status=403)
    return Response({"message": "Reports endpoint"})