from rest_framework import serializers
from home.models import normalusers
from tasks.models import Task

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = normalusers
        fields = ['id', 'name', 'email', 'password']

class TaskSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=normalusers.objects.all())

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'completed', 'priority', 'deadline', 'category', 'user', 'attachment', 'created_at', 'updated_at']          
        read_only_fields = ['created_at', 'updated_at']