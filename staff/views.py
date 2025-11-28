from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from appointments.models import Staff
from services.models import Service

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def staff_list(request):
    """List all staff with their specialties"""
    if not request.user.is_admin_user():
        return Response({'error': 'Admin access required'}, status=403)
    
    staff_members = Staff.objects.filter(is_active=True).select_related('user')
    
    staff_data = []
    for staff in staff_members:
        staff_data.append({
            'id': staff.id,
            'name': staff.user.get_full_name() or staff.user.username,
            'email': staff.user.email,
            'expertise': staff.expertise,
            'services': [service.name for service in staff.services.all()],
            'is_active': staff.is_active,
        })
    
    return Response(staff_data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def staff_create(request):
    """Create new staff member"""
    if not request.user.is_admin_user():
        return Response({'error': 'Admin access required'}, status=403)
    
    # Simple implementation - we'll enhance this later
    return Response({"message": "Staff creation endpoint - to be implemented"})