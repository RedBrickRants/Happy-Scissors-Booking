#serializers convert comlplex django models into python datatypes that can be 
#rendered into content types ike JSON to be passed to the front end though an API
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.apps import apps
from .models import CustomUser
from clients.models import Client

#this class will handle user registration
class UserRegistrationSerializer(serializers.ModelSerializer):
    #pasword fields 1 and 2 to confirm password, 
    #write only so they are not included in responses
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'password2', 'phone', 'user_type')
        
        #extra keyword arguments set default usertype to client for security
        extra_kwargs = {
            'user_type': {'default': 'client'}
        }

    #validation function checks if passwords match
    #method checks the passwords in the field attribute to see if they match(a) (get it?) 
    #and raises error if the dont (no appostorphe cus im a gangsta)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields dodent match."})#fis that typo
        return attrs

    #does what it says on the tin
    def create(self, validated_data):
        validated_data.pop('password2') #remove password2 from data as we dont need it anymore

        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone = validated_data.get('phone', ''), #optional field
            user_type = validated_data.get('user_type', 'client'), #default to client   
        )

        if user.user_type == 'client':
            Client = apps.get_model('clients', 'Client')
            Client.objects.create(user=user)
        return user
    
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'phone', 'user_type', 'date_joined')
        read_only_fields = ('id', 'user_type', 'date_joined')

class ClientProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = Client
        fields = ('id', 'user', 'preferences', 'loyalty_points', 'total_appointments')
        read_only_fields = ('id', 'loyalty_points', 'total_appointments')