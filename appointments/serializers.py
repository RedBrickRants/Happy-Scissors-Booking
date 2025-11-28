# appointments/serializers.py
from rest_framework import serializers
from .models import Staff, Appointment
from services.models import Service
from users.models import CustomUser
from clients.models import Client

class StaffSerializer(serializers.ModelSerializer):
    """Serializer for staff with user details"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    full_name = serializers.SerializerMethodField()
    services = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Service.objects.all(),
        required=False
    )
    service_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Staff
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'phone',
            'full_name', 'specialization', 'services', 'service_names',
            'is_active', 'maximum_daily_appointments'
        ]
        read_only_fields = ['id']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    
    def get_service_names(self, obj):
        return [service.name for service in obj.services.all()]


class StaffCreateSerializer(serializers.Serializer):
    """Serializer for creating new staff members"""
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=15, required=False, allow_blank=True)
    specialization = serializers.CharField(required=False, allow_blank=True)
    services = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    maximum_daily_appointments = serializers.IntegerField(default=10)
    
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value
    
    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("User with this username already exists.")
        return value
    
    def validate_services(self, value):
        if value:
            # Check if all service IDs exist
            existing_services = Service.objects.filter(id__in=value).count()
            if existing_services != len(value):
                raise serializers.ValidationError("One or more service IDs are invalid.")
        return value
    
    def create(self, validated_data):
        # Extract services list
        service_ids = validated_data.pop('services', [])
        
        # Create user account
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            user_type='staff'
        )
        
        # Create staff profile
        staff = Staff.objects.create(
            user=user,
            specialization=validated_data.get('specialization', ''),
            maximum_daily_appointments=validated_data.get('maximum_daily_appointments', 10),
            is_active=True
        )
        
        # Assign services
        if service_ids:
            services = Service.objects.filter(id__in=service_ids)
            staff.services.set(services)
        
        return staff


class StaffUpdateSerializer(serializers.Serializer):
    """Serializer for updating staff members"""
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    phone = serializers.CharField(max_length=15, required=False)
    email = serializers.EmailField(required=False)
    specialization = serializers.CharField(required=False, allow_blank=True)
    services = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    maximum_daily_appointments = serializers.IntegerField(required=False)
    is_active = serializers.BooleanField(required=False)
    
    def validate_email(self, value):
        # Check if email exists for another user
        instance = self.instance
        if CustomUser.objects.filter(email=value).exclude(id=instance.user.id).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value
    
    def validate_services(self, value):
        if value:
            existing_services = Service.objects.filter(id__in=value).count()
            if existing_services != len(value):
                raise serializers.ValidationError("One or more service IDs are invalid.")
        return value
    
    def update(self, instance, validated_data):
        # Update user fields
        user = instance.user
        if 'first_name' in validated_data:
            user.first_name = validated_data['first_name']
        if 'last_name' in validated_data:
            user.last_name = validated_data['last_name']
        if 'phone' in validated_data:
            user.phone = validated_data['phone']
        if 'email' in validated_data:
            user.email = validated_data['email']
        user.save()
        
        # Update staff fields
        if 'specialization' in validated_data:
            instance.specialization = validated_data['specialization']
        if 'maximum_daily_appointments' in validated_data:
            instance.maximum_daily_appointments = validated_data['maximum_daily_appointments']
        if 'is_active' in validated_data:
            instance.is_active = validated_data['is_active']
        instance.save()
        
        # Update services
        if 'services' in validated_data:
            services = Service.objects.filter(id__in=validated_data['services'])
            instance.services.set(services)
        
        return instance


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for appointments with full details"""
    client_name = serializers.CharField(source='client.user.get_full_name', read_only=True)
    client_email = serializers.CharField(source='client.user.email', read_only=True)
    client_phone = serializers.CharField(source='client.user.phone', read_only=True)
    staff_name = serializers.CharField(source='staff.user.get_full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_duration = serializers.IntegerField(source='service.duration', read_only=True)
    service_price = serializers.DecimalField(source='service.price', max_digits=8, decimal_places=2, read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'client', 'client_name', 'client_email', 'client_phone',
            'staff', 'staff_name', 'service', 'service_name', 
            'service_duration', 'service_price',
            'scheduled_time', 'end_time', 'status', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'end_time']


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appointments"""
    
    class Meta:
        model = Appointment
        fields = ['client', 'staff', 'service', 'scheduled_time', 'notes', 'status']
    
    def validate(self, data):
        """Validate appointment booking"""
        from django.utils import timezone
        from datetime import timedelta
        
        scheduled_time = data['scheduled_time']
        staff = data['staff']
        service = data['service']
        
        # Check if scheduled time is in the future
        if scheduled_time < timezone.now():
            raise serializers.ValidationError("Cannot book appointments in the past.")
        
        # Calculate end time
        end_time = scheduled_time + timedelta(minutes=service.duration)
        
        # Check for overlapping appointments for the same staff
        overlapping = Appointment.objects.filter(
            staff=staff,
            scheduled_time__lt=end_time,
            end_time__gt=scheduled_time,
            status__in=['pending', 'confirmed', 'in_progress']
        ).exclude(id=self.instance.id if self.instance else None)
        
        if overlapping.exists():
            raise serializers.ValidationError(
                f"Staff member {staff.user.get_full_name()} is not available at this time. "
                f"Conflicting appointment exists."
            )
        
        # Check if staff is qualified for this service
        if not staff.services.filter(id=service.id).exists():
            raise serializers.ValidationError(
                f"Staff member {staff.user.get_full_name()} is not qualified for {service.name}."
            )
        
        # Check staff is active
        if not staff.is_active:
            raise serializers.ValidationError(
                f"Staff member {staff.user.get_full_name()} is not currently available."
            )
        
        return data
    
    def create(self, validated_data):
        # The end_time will be auto-calculated in the model's save method
        appointment = Appointment.objects.create(**validated_data)
        return appointment


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating appointments"""
    
    class Meta:
        model = Appointment
        fields = ['staff', 'service', 'scheduled_time', 'status', 'notes']
    
    def validate(self, data):
        """Validate appointment updates"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Get current values or new values
        scheduled_time = data.get('scheduled_time', self.instance.scheduled_time)
        staff = data.get('staff', self.instance.staff)
        service = data.get('service', self.instance.service)
        
        # If scheduled_time or service changed, recalculate end_time and check conflicts
        if 'scheduled_time' in data or 'service' in data:
            end_time = scheduled_time + timedelta(minutes=service.duration)
            
            # Check for overlapping appointments
            overlapping = Appointment.objects.filter(
                staff=staff,
                scheduled_time__lt=end_time,
                end_time__gt=scheduled_time,
                status__in=['pending', 'confirmed', 'in_progress']
            ).exclude(id=self.instance.id)
            
            if overlapping.exists():
                raise serializers.ValidationError(
                    f"Staff member is not available at this time."
                )
        
        # Check if staff changed and new staff is qualified
        if 'staff' in data:
            service_to_check = data.get('service', self.instance.service)
            if not staff.services.filter(id=service_to_check.id).exists():
                raise serializers.ValidationError(
                    f"Staff member is not qualified for this service."
                )
        
        return data