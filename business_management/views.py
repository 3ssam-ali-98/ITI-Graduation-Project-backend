from rest_framework.decorators import api_view
# from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from business_management.models import Business
from business_management.serializers import BusinessSerializer
from business_management.filters import BusinessFilter
from .models import Tasks
from .serializers import TaskSerializer
from .models import Client
from .serializers import ClientSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import UserSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import update_last_login
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken


# Create your views here.

class TaskViewSet(viewsets.ModelViewSet):
	# queryset = Tasks.objects.all()
	serializer_class = TaskSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user 
		return Tasks.objects.filter(business=user.business)

	def perform_create(self, serializer):
			owner = self.request.user
			task = serializer.save(business=owner.business)
			task.save()

# class TaskViewSet(viewsets.ModelViewSet):
#     serializer_class = TaskSerializer

#     def get_queryset(self):
#         business_id = self.kwargs.get('business_id')
#         return Tasks.objects.filter(business__id=business_id)


class ClientViewSet(viewsets.ModelViewSet):
	# queryset = Client.objects.all()
	serializer_class = ClientSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user 
		return Client.objects.filter(business=user.business)

	def perform_create(self, serializer):
		owner = self.request.user
		client = serializer.save(business=owner.business)
		client.save()
    
class EmployeeViewSet(viewsets.ModelViewSet):
    
	serializer_class = UserSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user 
		return User.objects.filter(user_type="Employee", business=user.business)

	def perform_create(self, serializer):
		owner = self.request.user
		user = serializer.save()
		user.business = owner.business 
		user.save()


class UserListCreateView(generics.ListCreateAPIView):
	queryset = User.objects.filter(is_superuser=False, is_staff=False)
	serializer_class = UserSerializer
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = ['user_type']
	search_fields = ['username']

	def perform_create(self, serializer):
		user = serializer.save()
		business = Business.objects.create(name=self.request.data.get("business_name"), owner=user)
		user.business = business
		user.save()


class UserDetailView(APIView):
	def get(self, request, pk):
		user = get_object_or_404(User, pk=pk)
		serializer = UserSerializer(user)
		return Response(serializer.data)

	def put(self, request, pk):
		user = get_object_or_404(User, pk=pk)
		data = request.data.copy()
		data.pop("is_superuser", None)
		data.pop("is_staff", None)
		data.pop("email", None)	

		if "password" in data:
			data["password"] = make_password(data["password"])

		if "business_name" in data:
			if user.business:
				user.business.name = data["business_name"]
				user.business.save()
		
		serializer = UserSerializer(user, data=data)
  
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def patch(self, request, pk):
		user = get_object_or_404(User, pk=pk)
		data = request.data.copy()
		data.pop("is_superuser", None)
		data.pop("is_staff", None)
		data.pop("email", None)
  
		if "password" in data:
			data["password"] = make_password(data["password"])
   
		if "business_name" in data:
			if user.business:
				user.business.name = data["business_name"]
				user.business.save()
    
		serializer = UserSerializer(user, data=data, partial=True)
  
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk):
		user = get_object_or_404(User, pk=pk)
		user.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)
  
class BusinessView(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer   
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BusinessFilter
    search_fields = ["name", "owner"]  
    ordering_fields = ["name", "created_at"] 

class LoginView(APIView):
	def post(self, request):
		email = request.data.get("email")
		password = request.data.get("password")

		try:
			user = User.objects.get(email=email)  
			if user.check_password(password):  
				refresh = RefreshToken.for_user(user)
				return Response({"token": str(refresh.access_token), "refresh_token": str(refresh), "user_id": user.id , "user_type": user.user_type, "user_name": user.first_name}, status=status.HTTP_200_OK)
				# token, created = Token.objects.get_or_create(user=user)
				# return Response({"token": token.key, "user_id": user.id , "user_type": user.user_type, "user_name": user.first_name}, status=status.HTTP_200_OK)
		except User.DoesNotExist:
			pass

		return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def validate_password(request):
    user = request.user
    password = request.data.get("password")

    if user.check_password(password):
        return Response({"valid": True}, status=status.HTTP_200_OK)
    return Response({"valid": False}, status=status.HTTP_400_BAD_REQUEST)