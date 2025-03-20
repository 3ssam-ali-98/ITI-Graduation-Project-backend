from django.contrib import admin
from .models import Client, Business, Tasks, User 


admin.site.register(Client)
admin.site.register(Business)
admin.site.register(Tasks)
admin.site.register(User)
