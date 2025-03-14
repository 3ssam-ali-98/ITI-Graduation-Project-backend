# from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from business_management.models import Business
from business_management.serializers import BusinessSerializer
from business_management.filters import BusinessFilter

# Create your views here.
class BusinessView(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer   
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BusinessFilter
    search_fields = ["name", "owner"]  
    ordering_fields = ["name", "created_at"]  