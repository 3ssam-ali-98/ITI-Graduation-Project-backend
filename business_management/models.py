from django.db import models

# Create your models here.
class Business(models.Model):
    name = models.CharField(max_length=50)
    # owner = models.ForeignKey("User", related_name='buisness', on_delete=models.CASCADE, null=True) 
    
    def __str__(self):
        return self.name