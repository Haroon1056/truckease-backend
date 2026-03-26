from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import traceback
import sys

@csrf_exempt
def debug_admin_error(request):
    """Debug endpoint to capture the exact admin error"""
    try:
        from django.contrib import admin
        from django.contrib.admin.sites import site
        from django.contrib.auth.forms import UserCreationForm
        from .models import User
        
        # Get the admin class for User
        user_admin = site._registry.get(User)
        
        if not user_admin:
            return JsonResponse({
                'status': 'error',
                'message': 'User model is not registered in admin'
            }, status=500)
        
        # Try to create the form using the admin's get_form method
        try:
            # Get the form class that the admin uses
            form_class = user_admin.get_form(request)
            # Try to instantiate it
            form = form_class()
            
            return JsonResponse({
                'status': 'success',
                'admin_class': str(user_admin.__class__),
                'form_fields': list(form.fields.keys()) if hasattr(form, 'fields') else [],
                'model_fields': [f.name for f in User._meta.fields],
                'message': 'Admin form created successfully'
            })
        except Exception as form_error:
            # Capture the actual admin form error
            return JsonResponse({
                'status': 'error',
                'error_type': type(form_error).__name__,
                'error_message': str(form_error),
                'traceback': traceback.format_exc().split('\n'),
                'admin_class': str(user_admin.__class__),
                'model_fields': [f.name for f in User._meta.fields]
            }, status=500)
            
    except Exception as e:
        # Capture the full error
        error_details = {
            'error_type': type(e).__name__,
            'error_message': str(e),
            'traceback': traceback.format_exc().split('\n'),
            'python_version': sys.version,
            'django_version': __import__('django').get_version()
        }
        return JsonResponse(error_details, status=500)
    
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def simple_admin_test(request):
    """Simple test to see if admin is accessible"""
    try:
        from django.contrib import admin
        from .models import User
        
        # Try to get the admin URL for adding a user
        from django.urls import reverse
        
        return HttpResponse(f"""
        <html>
        <body>
            <h1>Admin Test</h1>
            <p>User model fields: {[f.name for f in User._meta.fields]}</p>
            <p>User admin registered: {admin.site._registry.get(User) is not None}</p>
            <p>Admin URL: /admin/accounts/user/</p>
            <p><a href="/admin/accounts/user/add/">Try to add user directly</a></p>
        </body>
        </html>
        """)
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)

class RegisterView(APIView):
    """User registration view"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            print("="*50)
            print("Registration attempt:")
            print("Request data:", request.data)
            print("="*50)
            
            serializer = RegisterSerializer(data=request.data)
            
            if serializer.is_valid():
                user = serializer.save()
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'message': 'Registration successful',
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'user_type': user.user_type,
                        'phone_number': user.phone_number,
                    },
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                }, status=status.HTTP_201_CREATED)
            
            print("Validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except IntegrityError as e:
            print("Integrity Error:", e)
            return Response({
                'error': 'Database error',
                'detail': 'Email or phone number already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Unexpected error:", e)
            return Response({
                'error': 'Registration failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """User login view"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            
            if serializer.is_valid():
                email = serializer.validated_data['email']
                password = serializer.validated_data['password']
                
                # Authenticate user (using email)
                user = authenticate(username=email, password=password)
                
                if user:
                    # Generate JWT tokens
                    refresh = RefreshToken.for_user(user)
                    
                    return Response({
                        'message': 'Login successful',
                        'user': {
                            'id': user.id,
                            'email': user.email,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'user_type': user.user_type,
                            'phone_number': user.phone_number,
                        },
                        'tokens': {
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                        }
                    }, status=status.HTTP_200_OK)
                
                return Response({
                    'error': 'Invalid email or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print("Login error:", e)
            return Response({
                'error': 'Login failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    """Get and update user profile"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current user profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """Update user profile"""
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)