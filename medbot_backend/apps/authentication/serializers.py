from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from apps.users.models import User, PatientProfile, DoctorProfile


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes user information.
    """
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add custom user data to the token response
        data.update({
            'user': {
                'id': str(self.user.id),
                'username': self.user.username,
                'email': self.user.email,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'user_type': self.user.user_type,
                'is_verified': self.user.is_verified,
            }
        })
        
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'user_type', 'phone_number',
            'date_of_birth', 'gender'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Create profile based on user type
        if user.user_type == 'patient':
            PatientProfile.objects.create(user=user)
        elif user.user_type == 'doctor':
            # Doctor profile will be created separately with additional info
            pass
            
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information.
    """
    patient_profile = serializers.SerializerMethodField()
    doctor_profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'user_type', 'phone_number', 'date_of_birth', 'gender',
            'emergency_contact', 'medical_history', 'allergies',
            'current_medications', 'preferred_language', 'is_verified',
            'patient_profile', 'doctor_profile'
        ]
        read_only_fields = ['id', 'username', 'user_type']
    
    def get_patient_profile(self, obj):
        if hasattr(obj, 'patient_profile'):
            return {
                'insurance_provider': obj.patient_profile.insurance_provider,
                'insurance_number': obj.patient_profile.insurance_number,
                'primary_care_physician': obj.patient_profile.primary_care_physician,
            }
        return None
    
    def get_doctor_profile(self, obj):
        if hasattr(obj, 'doctor_profile'):
            return {
                'license_number': obj.doctor_profile.license_number,
                'specialization': obj.doctor_profile.specialization.name,
                'years_of_experience': obj.doctor_profile.years_of_experience,
                'consultation_fee': obj.doctor_profile.consultation_fee,
                'is_available': obj.doctor_profile.is_available,
                'rating': obj.doctor_profile.rating,
            }
        return None


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
