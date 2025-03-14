from rest_framework import serializers
from .models import Tasks
from .models import Client

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client

        fields = '__all__'
