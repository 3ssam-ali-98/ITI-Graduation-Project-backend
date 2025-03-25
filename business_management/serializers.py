from rest_framework import serializers
from .models import Task
from .models import Client
from business_management.models import User
from business_management.models import Business


class TaskSerializer(serializers.ModelSerializer):
    assigned_employee = serializers.SerializerMethodField()
    class Meta:
        model = Task
        fields = '__all__'
        
    def get_assigned_employee(self, obj):
        """Return the full name of the assigned employee."""
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
        return None    

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client

        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
	business_name = serializers.CharField(source="business.name", read_only=True)
	password = serializers.CharField(write_only=True, required=True)
	class Meta:
		model = User
		fields = '__all__'
		extra_kwargs = {'password': {'write_only': True}}

	def validate_user_type(self, value):
		allowed_types = ["Business Owner", "Employee"]
		if value not in allowed_types:
			raise serializers.ValidationError("Invalid user type. Choose 'Business Owner' or 'Employee'.")
		return value

	def validate_email(self, value):
		if User.objects.filter(email=value).exists():
			raise serializers.ValidationError("Email already exists.")
		return value

	def create(self, validated_data):
		password = validated_data.pop('password')  
		user = User(**validated_data)  
		user.set_password(password)  
		user.is_superuser = False
		user.is_staff = False
		user.save()
		return user

  
class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__' 

