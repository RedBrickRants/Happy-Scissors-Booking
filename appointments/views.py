# appointments/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Appointment, Staff
from appointments.serializers import (
    AppointmentSerializer, 
    AppointmentCreateSerializer,
    AppointmentUpdateSerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_list(request):
    """List appointments based on user role"""
    user = request.user
    
    # Get query parameters
    status_filter = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    staff_id = request.GET.get('staff_id')
    
    # Base query based on user role
    if user.is_admin_user():
        # Admin sees all appointments
        appointments = Appointment.objects.all()
    elif user.user_type == 'staff':
        # Staff sees only their appointments
        try:
            staff = Staff.objects.get(user=user)
            appointments = Appointment.objects.filter(staff=staff)
        except Staff.DoesNotExist:
            return Response(
                {'error': 'Staff profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    elif user.user_type == 'client':
        # Client sees only their appointments
        try:
            appointments = Appointment.objects.filter(client__user=user)
        except:
            return Response(
                {'error': 'Client profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        return Response(
            {'error': 'Invalid user type'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Apply filters
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            appointments = appointments.filter(scheduled_time__gte=date_from_obj)
        except ValueError:
            return Response(
                {'error': 'Invalid date_from format. Use YYYY-MM-DD'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            # Add one day to include the entire end date
            date_to_obj = date_to_obj + timedelta(days=1)
            appointments = appointments.filter(scheduled_time__lt=date_to_obj)
        except ValueError:
            return Response(
                {'error': 'Invalid date_to format. Use YYYY-MM-DD'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    if staff_id and user.is_admin_user():
        appointments = appointments.filter(staff_id=staff_id)
    
    # Optimize query
    appointments = appointments.select_related(
        'client__user', 'staff__user', 'service'
    ).order_by('-scheduled_time')
    
    serializer = AppointmentSerializer(appointments, many=True)
    
    return Response({
        'count': len(serializer.data),
        'appointments': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_appointment(request):
    """Create a new appointment"""
    # Only admin and clients can create appointments
    if not (request.user.is_admin_user() or request.user.user_type == 'client'):
        return Response(
            {'error': 'Only clients and admins can book appointments'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = AppointmentCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        appointment = serializer.save()
        
        # Return full appointment details
        appointment_serializer = AppointmentSerializer(appointment)
        
        return Response({
            'message': 'Appointment created successfully',
            'appointment': appointment_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def appointment_detail(request, appointment_id):
    """Get, update, or delete a specific appointment"""
    try:
        appointment = Appointment.objects.select_related(
            'client__user', 'staff__user', 'service'
        ).get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response(
            {'error': 'Appointment not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions
    user = request.user
    if not user.is_admin_user():
        # Staff can view/update their own appointments
        if user.user_type == 'staff':
            try:
                staff = Staff.objects.get(user=user)
                if appointment.staff != staff:
                    return Response(
                        {'error': 'You can only access your own appointments'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Staff.DoesNotExist:
                return Response(
                    {'error': 'Staff profile not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        # Clients can only view their own appointments
        elif user.user_type == 'client':
            if appointment.client.user != user:
                return Response(
                    {'error': 'You can only access your own appointments'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
    
    if request.method == 'GET':
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # Only admin can fully update appointments
        if not user.is_admin_user():
            return Response(
                {'error': 'Only admins can update appointment details'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = AppointmentUpdateSerializer(
            appointment, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            updated_appointment = serializer.save()
            appointment_serializer = AppointmentSerializer(updated_appointment)
            
            return Response({
                'message': 'Appointment updated successfully',
                'appointment': appointment_serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Admin or client can cancel (set status to canceled)
        if user.is_admin_user() or (user.user_type == 'client' and appointment.client.user == user):
            appointment.status = 'canceled'
            appointment.save()
            
            return Response({
                'message': 'Appointment canceled successfully',
                'appointment_id': appointment_id
            })
        
        return Response(
            {'error': 'You do not have permission to cancel this appointment'}, 
            status=status.HTTP_403_FORBIDDEN
        )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_appointment_status(request, appointment_id):
    """Update appointment status only"""
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response(
            {'error': 'Appointment not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    user = request.user
    
    # Check permissions
    if not user.is_admin_user():
        # Staff can update status of their own appointments
        if user.user_type == 'staff':
            try:
                staff = Staff.objects.get(user=user)
                if appointment.staff != staff:
                    return Response(
                        {'error': 'You can only update your own appointments'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Staff.DoesNotExist:
                return Response(
                    {'error': 'Staff profile not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            return Response(
                {'error': 'Only staff and admins can update appointment status'}, 
                status=status.HTTP_403_FORBIDDEN
            )
    
    new_status = request.data.get('status')
    
    if not new_status:
        return Response(
            {'error': 'Status is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate status
    valid_statuses = ['pending', 'confirmed', 'in_progress', 'completed', 'canceled', 'no_show']
    if new_status not in valid_statuses:
        return Response(
            {'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    appointment.status = new_status
    appointment.save()
    
    serializer = AppointmentSerializer(appointment)
    
    return Response({
        'message': 'Appointment status updated successfully',
        'appointment': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def today_appointments(request):
    """Get today's appointments"""
    if not request.user.is_admin_user():
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    today = timezone.now().date()
    
    appointments = Appointment.objects.filter(
        scheduled_time__date=today
    ).select_related('client__user', 'staff__user', 'service').order_by('scheduled_time')
    
    serializer = AppointmentSerializer(appointments, many=True)
    
    # Group by status
    by_status = {
        'pending': [],
        'confirmed': [],
        'in_progress': [],
        'completed': [],
        'canceled': [],
        'no_show': []
    }
    
    for apt in serializer.data:
        by_status[apt['status']].append(apt)
    
    return Response({
        'date': today.isoformat(),
        'total': len(serializer.data),
        'by_status': by_status,
        'all_appointments': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def upcoming_appointments(request):
    """Get upcoming appointments"""
    user = request.user
    
    # Get days parameter (default 7)
    try:
        days = int(request.GET.get('days', 7))
    except ValueError:
        days = 7
    
    now = timezone.now()
    end_date = now + timedelta(days=days)
    
    # Filter based on user role
    if user.is_admin_user():
        appointments = Appointment.objects.filter(
            scheduled_time__gte=now,
            scheduled_time__lte=end_date,
            status__in=['pending', 'confirmed']
        )
    elif user.user_type == 'staff':
        try:
            staff = Staff.objects.get(user=user)
            appointments = Appointment.objects.filter(
                staff=staff,
                scheduled_time__gte=now,
                scheduled_time__lte=end_date,
                status__in=['pending', 'confirmed']
            )
        except Staff.DoesNotExist:
            return Response(
                {'error': 'Staff profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    elif user.user_type == 'client':
        appointments = Appointment.objects.filter(
            client__user=user,
            scheduled_time__gte=now,
            scheduled_time__lte=end_date,
            status__in=['pending', 'confirmed']
        )
    else:
        return Response(
            {'error': 'Invalid user type'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    appointments = appointments.select_related(
        'client__user', 'staff__user', 'service'
    ).order_by('scheduled_time')
    
    serializer = AppointmentSerializer(appointments, many=True)
    
    return Response({
        'period': {
            'start': now.isoformat(),
            'end': end_date.isoformat(),
            'days': days
        },
        'count': len(serializer.data),
        'appointments': serializer.data
    })