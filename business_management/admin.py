from django.contrib import admin
from .models import Client, Business, Task, User 


admin.site.register(Client)
admin.site.register(Business)
admin.site.register(Task)
admin.site.register(User)
