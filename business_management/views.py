# from django.shortcuts import render
from rest_framework import viewsets

from business_management.models import Business
from business_management.serializers import BusinessSerializer

# Create your views here.
class BusinessView(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer   