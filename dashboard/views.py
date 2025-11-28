# dashboard/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import datetime, timedelta
from appointments.models import Appointment, Staff
from services.models import Service
from clients.models import Client


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_overview(request):
    """Main dashboard overview with key metrics"""
    if not request.user.is_admin_user():
        return Response({'error': 'Admin access required'}, status=403)
    
    today = timezone.now().date()
    now = timezone.now()
    
    # Today's appointments
    today_appointments = Appointment.objects.filter(scheduled_time__date=today)
    today_count = today_appointments.count()
    today_pending = today_appointments.filter(status='pending').count()
    today_confirmed = today_appointments.filter(status='confirmed').count()
    today_completed = today_appointments.filter(status='completed').count()
    today_in_progress = today_appointments.filter(status='in_progress').count()
    
    # Staff metrics
    total_staff = Staff.objects.filter(is_active=True).count()
    staff_on_duty_today = Staff.objects.filter(
        is_active=True,
        appointment__scheduled_time__date=today
    ).distinct().count()
    
    # This week's appointments
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=7)
    week_appointments = Appointment.objects.filter(
        scheduled_time__date__gte=week_start,
        scheduled_time__date__lt=week_end
    ).count()
    
    # Revenue today (completed appointments)
    today_revenue = Appointment.objects.filter(
        scheduled_time__date=today,
        status='completed'
    ).aggregate(
        total=Sum('service__price')
    )['total'] or 0
    
    # Upcoming appointments (next 7 days)
    upcoming = Appointment.objects.filter(
        scheduled_time__gte=now,
        scheduled_time__lte=now + timedelta(days=7),
        status__in=['pending', 'confirmed']
    ).count()
    
    # Total clients
    total_clients = Client.objects.count()
    
    # Recent appointments for quick view
    recent_appointments = Appointment.objects.filter(
        scheduled_time__date=today
    ).select_related('client__user', 'staff__user', 'service').order_by('scheduled_time')[:10]
    
    recent_data = []
    for apt in recent_appointments:
        recent_data.append({
            'id': apt.id,
            'client': apt.client.user.get_full_name() or apt.client.user.username,
            'staff': apt.staff.user.get_full_name() or apt.staff.user.username,
            'service': apt.service.name,
            'time': apt.scheduled_time.strftime('%H:%M'),
            'status': apt.status
        })
    
    return Response({
        'overview': {
            'today_date': today.isoformat(),
            'total_staff': total_staff,
            'staff_on_duty_today': staff_on_duty_today,
            'total_clients': total_clients,
            'active_services': Service.objects.filter(active=True).count()
        },
        'today': {
            'total_appointments': today_count,
            'pending': today_pending,
            'confirmed': today_confirmed,
            'in_progress': today_in_progress,
            'completed': today_completed,
            'revenue': float(today_revenue)
        },
        'week': {
            'appointments': week_appointments,
            'start_date': week_start.isoformat(),
            'end_date': week_end.isoformat()
        },
        'upcoming': {
            'next_7_days': upcoming
        },
        'recent_appointments': recent_data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Detailed dashboard statistics"""
    if not request.user.is_admin_user():
        return Response({'error': 'Admin access required'}, status=403)
    
    today = timezone.now().date()
    
    # Get date range from query params
    period = request.GET.get('period', 'week')  # week, month, year
    
    if period == 'week':
        start_date = today - timedelta(days=7)
    elif period == 'month':
        start_date = today - timedelta(days=30)
    elif period == 'year':
        start_date = today - timedelta(days=365)
    else:
        start_date = today - timedelta(days=7)
    
    # Appointments in period
    appointments = Appointment.objects.filter(
        scheduled_time__date__gte=start_date,
        scheduled_time__date__lte=today
    )
    
    # Status breakdown
    status_counts = appointments.values('status').annotate(count=Count('id'))
    status_breakdown = {item['status']: item['count'] for item in status_counts}
    
    # Top services
    top_services = appointments.values('service__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Top staff by appointments
    top_staff = appointments.values('staff__user__first_name', 'staff__user__last_name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Revenue by status
    revenue = appointments.filter(status='completed').aggregate(
        total=Sum('service__price')
    )['total'] or 0
    
    return Response({
        'period': {
            'type': period,
            'start_date': start_date.isoformat(),
            'end_date': today.isoformat()
        },
        'totals': {
            'appointments': appointments.count(),
            'completed': appointments.filter(status='completed').count(),
            'revenue': float(revenue)
        },
        'status_breakdown': status_breakdown,
        'top_services': list(top_services),
        'top_staff': list(top_staff)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def calendar_view(request):
    """Enhanced calendar view with appointments"""
    if not request.user.is_admin_user():
        return Response({'error': 'Admin access required'}, status=403)
    
    # Get date range from query params
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                status=400
            )
    else:
        # Default to current month
        start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Get last day of month
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1)
    
    # Get appointments in range
    appointments = Appointment.objects.filter(
        scheduled_time__range=[start_date, end_date]
    ).select_related('client__user', 'staff__user', 'service')
    
    calendar_data = []
    for appointment in appointments:
        calendar_data.append({
            'id': appointment.id,
            'title': f"{appointment.service.name} - {appointment.client.user.get_full_name() or appointment.client.user.username}",
            'client': appointment.client.user.get_full_name() or appointment.client.user.username,
            'client_id': appointment.client.id,
            'staff': appointment.staff.user.get_full_name() or appointment.staff.user.username,
            'staff_id': appointment.staff.id,
            'service': appointment.service.name,
            'service_id': appointment.service.id,
            'start': appointment.scheduled_time.isoformat(),
            'end': appointment.end_time.isoformat() if appointment.end_time else None,
            'status': appointment.status,
            'notes': appointment.notes,
            'color': get_status_color(appointment.status)
        })
    
    # Group by date for easy daily view
    by_date = {}
    for apt in calendar_data:
        date = apt['start'].split('T')[0]
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(apt)
    
    return Response({
        'period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'total_appointments': len(calendar_data),
        'appointments': calendar_data,
        'by_date': by_date
    })


def get_status_color(status):
    """Get color code for appointment status"""
    colors = {
        'pending': '#FFA500',      # Orange
        'confirmed': '#4CAF50',    # Green
        'in_progress': '#2196F3',  # Blue
        'completed': '#9E9E9E',    # Gray
        'canceled': '#F44336',     # Red
        'no_show': '#FF5722'       # Deep Orange
    }
    return colors.get(status, '#000000')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def staff_performance(request):
    """Staff performance metrics"""
    if not request.user.is_admin_user():
        return Response({'error': 'Admin access required'}, status=403)
    
    # Get date range
    period = request.GET.get('period', 'month')
    today = timezone.now().date()
    
    if period == 'week':
        start_date = today - timedelta(days=7)
    elif period == 'month':
        start_date = today - timedelta(days=30)
    else:
        start_date = today - timedelta(days=30)
    
    # Get all active staff
    staff_members = Staff.objects.filter(is_active=True)
    
    performance_data = []
    for staff in staff_members:
        appointments = Appointment.objects.filter(
            staff=staff,
            scheduled_time__date__gte=start_date,
            scheduled_time__date__lte=today
        )
        
        total_appointments = appointments.count()
        completed = appointments.filter(status='completed').count()
        revenue = appointments.filter(status='completed').aggregate(
            total=Sum('service__price')
        )['total'] or 0
        
        performance_data.append({
            'staff_id': staff.id,
            'name': staff.user.get_full_name() or staff.user.username,
            'specialization': staff.specialization,
            'total_appointments': total_appointments,
            'completed_appointments': completed,
            'completion_rate': round((completed / total_appointments * 100) if total_appointments > 0 else 0, 2),
            'revenue': float(revenue),
            'services': [s.name for s in staff.services.all()]
        })
    
    # Sort by total appointments
    performance_data.sort(key=lambda x: x['total_appointments'], reverse=True)
    
    return Response({
        'period': {
            'type': period,
            'start_date': start_date.isoformat(),
            'end_date': today.isoformat()
        },
        'staff_performance': performance_data
    })