from django.shortcuts import render
from rest_framework import viewsets
from .models import Tasks
from .serializers import TaskSerializer
from .models import Client
from .serializers import ClientSerializer

from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import UserSerializer
from django_filters.rest_framework import DjangoFilterBackend


# Create your views here.

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Tasks.objects.all()
    serializer_class = TaskSerializer

# class TaskViewSet(viewsets.ModelViewSet):
#     serializer_class = TaskSerializer

#     def get_queryset(self):
#         business_id = self.kwargs.get('business_id')
#         return Tasks.objects.filter(business__id=business_id)


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class UserListCreateView(generics.ListCreateAPIView):
	queryset = User.objects.filter(is_superuser=False, is_staff=False)
	serializer_class = UserSerializer
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = ['user_type']
	search_fields = ['username']

	def perform_create(self, serializer):
		serializer.save(is_superuser=False, is_staff=False)


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
		serializer = UserSerializer(user, data=data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk):
		user = get_object_or_404(User, pk=pk)
		user.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

