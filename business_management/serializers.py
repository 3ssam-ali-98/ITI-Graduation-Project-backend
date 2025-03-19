from rest_framework import serializers







from .models import Tasks
from .models import Client
from business_management.models import User
from business_management.models import Business


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client

        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
	business_name = serializers.CharField(source="business.name", read_only=True)
	password = serializers.SerializerMethodField()
	class Meta:
		model = User
		fields = '__all__'

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
		validated_data["is_superuser"] = False
		validated_data["is_staff"] = False
		return super().create(validated_data)

	def get_password(self, obj):
		return "********"
  
class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__' 

