from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'first_name', 
                  'last_name', 'user_type', 'phone_number']
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        
        if data['user_type'] not in ['customer', 'driver']:
            raise serializers.ValidationError({"user_type": "Must be customer or driver"})
        
        # Check if email already exists
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Email already exists"})
        
        # Check if phone number already exists (if provided)
        if data.get('phone_number') and User.objects.filter(phone_number=data['phone_number']).exists():
            raise serializers.ValidationError({"phone_number": "Phone number already exists"})
        
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'user_type', 
                  'phone_number', 'profile_picture', 'is_verified', 'created_at']
        read_only_fields = ['id', 'created_at']