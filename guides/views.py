from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from home.forms import UserForm
from home.models import normalusers
from api.serializers import UserSerializer, TaskSerializer
from tasks.models import Task
from rest_framework import viewsets
# Create your views here.

class register(APIView):
    def post(self, request):
        form = UserForm(request.data)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = normalusers.objects.create(name=name, email=email, password=password)
            user.save()

            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)



class login(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = normalusers.objects.filter(email=email).first()

        if user and user.password == password:  

            return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    
class TaskView(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer    