from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
	first_name = models.CharField(max_length=50, blank=True, null=True)
	last_name = models.CharField(max_length=50, blank=True, null=True)
	username = models.CharField(max_length=50, unique=True)
	email = models.EmailField(unique=True)
	mobile_phone = models.CharField(max_length=11, unique=True, null=True, blank=True)
	profile_picture = models.FileField(upload_to='media/', blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	birthdate = models.DateField(null=True, blank=True)
	facebook_profile = models.URLField(max_length=255, null=True, blank=True)
	country = models.CharField(max_length=100, null=True, blank=True)

	def __str__(self):
		return f'{self.username}'


class Token(models.Model):
	token = models.CharField(max_length=250, unique=True)
	user = models.OneToOneField(User, related_name='tokens', on_delete=models.CASCADE)


class Project(models.Model):
	title = models.CharField(max_length=255, default="Project")
	details = models.TextField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	total_target = models.IntegerField() 
	start_time = models.DateTimeField(null=True, blank=True)
	end_time = models.DateTimeField(null=True, blank=True)
	owner = models.ForeignKey("User", related_name='projects', on_delete=models.CASCADE, null=True)
	category = models.ForeignKey("Category", related_name='projects', on_delete=models.SET_NULL, null=True, blank=True)
	tags = models.ManyToManyField("Tag", blank=True, related_name="projects")
	featuerd = models.BooleanField(default=False)

	class Meta:
		ordering = ("title",)

	def __str__(self):
		return f'{self.title}'


class Donation(models.Model):
	amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
	donated_by = models.ForeignKey('User', related_name='donations', on_delete=models.SET_NULL, null=True)
	project = models.ForeignKey('Project', related_name='donations', on_delete=models.CASCADE)
	donation_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name_plural = "donations"
		ordering = ("donation_date",)

	def __str__(self):
		return 'Donation of {} by {} for project {}'.format(self.amount, self.donated_by, self.project)


class Category(models.Model):
	name = models.CharField(max_length=50, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name_plural = "categories"
		ordering = ("name",)

	def __str__(self):
		return f'{self.name}'


class Comment(models.Model):
	content = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	project = models.ForeignKey('Project' , related_name='comments',on_delete=models.CASCADE)
	user = models.ForeignKey("User", related_name='comments', on_delete=models.CASCADE)

	class Meta:
		verbose_name_plural = "Comments"
		ordering = ("created_at",)

	def __str__(self):
		return f'Comment {self.id}, by {self.user} on Project {self.project}'


class Rate(models.Model):
	rate = models.IntegerField(choices=((1, 1), (2, 2), (3, 3), (4, 4), (5, 5)))
	rated_by = models.ForeignKey('User', related_name='rated_projects', on_delete=models.CASCADE)	
	project = models.ForeignKey('Project', related_name='rating', on_delete=models.CASCADE)

	def __str__(self):
		return f'Rating by user {self.rated_by} on project {self.project}'


class Reply(models.Model):
	content = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey('User', related_name='replies', on_delete=models.CASCADE)
	comment = models.ForeignKey('Comment', related_name='replies', on_delete=models.CASCADE)

	class Meta:
		verbose_name_plural = "replies"
		ordering = ("created_at",)

	def __str__(self):
		return f'Reply on comment {self.comment} by user {self.user}'


class Picture(models.Model):
	image = models.FileField(upload_to='media/')
	created_at = models.DateTimeField(auto_now_add=True)
	project = models.ForeignKey("Project", related_name="pictures", on_delete=models.CASCADE)

	class Meta:
		verbose_name_plural = "pictures"
		ordering = ("created_at",)

	def __str__(self):
		return f'Picture {self.id} on project {self.project}'


class Report(models.Model):
	reported_by = models.ForeignKey("User", on_delete=models.CASCADE, related_name="reports")
	project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="reports", null=True)
	comment = models.ForeignKey("Comment", on_delete=models.CASCADE, related_name="reports", null=True)
	reason = models.TextField(blank=True, null=True)  
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Report by {self.reported_by} on comment {self.comment} on project {self.project}"		


class Tag(models.Model):
	name = models.CharField(max_length=50, unique=True)
	def __str__(self):
		return f'{self.name}'

