from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view that includes user information.
    """
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """
    Register new user with role-based setup.
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'User registered successfully',
            'user_id': str(user.id),
            'user_type': user.user_type,
            'username': user.username,
            'email': user.email
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    Get and update user profile information.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get current user profile"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        """Update user profile"""
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    Change user password.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_user(request):
    """
    Verify user account with additional documentation.
    This would typically involve document upload and admin approval.
    """
    user = request.user

    # In a real implementation, this would involve:
    # 1. Document upload verification
    # 2. Admin review process
    # 3. Background checks for healthcare providers

    # For now, we'll just mark as verified (development only)
    if not user.is_verified:
        user.is_verified = True
        user.save()
        return Response({
            'message': 'User verification initiated',
            'status': 'pending_review'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'message': 'User already verified'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_status(request):
    """
    Get current user status and permissions.
    """
    user = request.user
    return Response({
        'user_id': str(user.id),
        'username': user.username,
        'user_type': user.user_type,
        'is_verified': user.is_verified,
        'is_active': user.is_active,
        'permissions': {
            'can_create_consultations': user.user_type == 'patient',
            'can_manage_appointments': user.user_type in ['doctor', 'nurse', 'clinic_admin'],
            'can_access_admin': user.user_type == 'admin',
            'can_access_clinic_dashboard': user.user_type in ['clinic_admin', 'doctor', 'nurse'],
        }
    })
