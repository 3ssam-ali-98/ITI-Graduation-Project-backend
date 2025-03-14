from django.db import models

# Create your models here.

class Tasks(models.Model):
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

    # business = models.OneToOneField(Business, on_delete=models.CASCADE)
    # assigned_to = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
