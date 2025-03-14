from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet
from .views import ClientViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
router.register(r'clients', ClientViewSet)

# router.register(r'business/(?P<business_id>\d+)/tasks', TaskViewSet, basename='tasks')



urlpatterns = [
    path('', include(router.urls)),
]
