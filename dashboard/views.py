from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta
from appointments.models import Appointment
from appointments.models import Staff  

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_overview(request):
    """Main dashboard view"""
    if not request.user.is_admin_user():
        return Response({'error': 'Admin access required'}, status=403)
    return Response({"message": "Owner Dashboard - Calendar and Overview"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Basic dashboard statistics"""
    if not request.user.is_admin_user():
        return Response({'error': 'Admin access required'}, status=403)
    
    today = timezone.now().date()
    
    stats = {
        'today_appointments': Appointment.objects.filter(scheduled_time__date=today).count(),
        'total_staff': Staff.objects.filter(is_active=True).count(),
        'pending_appointments': Appointment.objects.filter(status='pending').count(),
    }
    return Response(stats)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def calendar_view(request):
    """Calendar view with appointments"""
    if not request.user.is_admin_user():
        return Response({'error': 'Admin access required'}, status=403)
    
    # Get appointments for the next 30 days
    start_date = timezone.now()
    end_date = start_date + timedelta(days=30)
    
    appointments = Appointment.objects.filter(
        scheduled_time__range=[start_date, end_date]
    ).select_related('client__user', 'staff__user', 'service')
    
    calendar_data = []
    for appointment in appointments:
        calendar_data.append({
            'id': appointment.id,
            'title': f"{appointment.service.name} - {appointment.client.user.username}",
            'start': appointment.scheduled_time.isoformat(),
            'end': appointment.end_time.isoformat() if appointment.end_time else None,
            'staff': appointment.staff.user.username,
            'status': appointment.status,
        })
    
    return Response(calendar_data)