# api/views.py

from django.contrib.auth import get_user_model, authenticate
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse

from .models import Profile

User = get_user_model()


def home(request):
    return HttpResponse("Please Check Postman Documention in Github README.md for more information")

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        mobile_number = request.data.get('mobile_number')
        first_name = request.data.get('first_name') 
        last_name = request.data.get('last_name')     

        # Validate required fields
        if not email  or not password or not mobile_number or not first_name or not last_name:
            return JsonResponse({'error': 'Email, username, password, mobile number, first name, and last name are required.'}, 
                                status=status.HTTP_400_BAD_REQUEST)

        # Check for existing email
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

     
        user = User(email=email, username=email, first_name=first_name, last_name=last_name)  
        user.set_password(password)
        user.save()

        
        Profile.objects.create(user=user, mobile_number=mobile_number)
        
        return JsonResponse({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return JsonResponse({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the user by email
            user = User.objects.get(email=email)

            # Check if the provided password is correct
            if user.check_password(password):
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                
                # Return tokens and user details
                return JsonResponse({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'name': user.first_name+ " "+user.last_name,
                        'phone_number': user.profile.mobile_number
                    }
                }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)