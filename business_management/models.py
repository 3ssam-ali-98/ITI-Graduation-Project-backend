from django.db import models
from django.contrib.auth.models import AbstractUser


class Client(models.Model):
	name = models.CharField(max_length=255)
	email = models.EmailField(unique=True)
	phone = models.CharField(max_length=20, unique=True)
	address = models.TextField(blank=True, null=True)
	notes = models.CharField(max_length=255, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	business = models.ForeignKey("Business", related_name='clients', on_delete=models.CASCADE, null=True) 

	def __str__(self):
		return self.name


class Business(models.Model):
	name = models.CharField(max_length=50)
	owner = models.OneToOneField("User", related_name='buisnesses', on_delete=models.CASCADE, null=True) 

	def __str__(self):
		return self.name


class Task(models.Model):
	PRIORITY_CHOICES = [
		("Low", "Low"),
		("Medium", "Medium"),
		("High", "High"),
	]

	name = models.CharField(max_length=255)
	description = models.TextField()
	priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="Medium")
	deadline = models.DateTimeField()
	completed = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	business = models.ForeignKey("Business", related_name='tasks', on_delete=models.CASCADE, null=True) 
	assigned_to = models.ForeignKey("User", related_name='tasks', on_delete=models.SET_NULL, null=True) 

	def __str__(self):
		return self.name


class User(AbstractUser):
	first_name = models.CharField(max_length=50, blank=True, null=True)
	last_name = models.CharField(max_length=50, blank=True, null=True)
	username = models.CharField(max_length=50, unique=True)
	user_type = models.CharField(max_length=20, choices=(('Business Owner', 'Business Owner'), ('Employee', 'Employee'), ('', '')))
	email = models.EmailField(unique=True)
	mobile_phone = models.CharField(max_length=11, unique=True, null=True, blank=True)
	profile_picture = models.FileField(upload_to='media/', blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	business = models.ForeignKey("Business", related_name='users', on_delete=models.CASCADE, null=True)

	def __str__(self):
		return f'{self.first_name} {self.last_name} - {self.username}'


class Token(models.Model):
	token = models.CharField(max_length=250, unique=True)
	user = models.OneToOneField(User, related_name='tokens', on_delete=models.CASCADE)

