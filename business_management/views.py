from django.shortcuts import render
from rest_framework import viewsets
from .models import Tasks
from .serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Tasks.objects.all()
    serializer_class = TaskSerializer

# class TaskViewSet(viewsets.ModelViewSet):
#     serializer_class = TaskSerializer

#     def get_queryset(self):
#         business_id = self.kwargs.get('business_id')
#         return Tasks.objects.filter(business__id=business_id)
