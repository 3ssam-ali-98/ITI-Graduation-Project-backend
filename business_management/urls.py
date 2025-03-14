from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)

# router.register(r'business/(?P<business_id>\d+)/tasks', TaskViewSet, basename='tasks')

urlpatterns = [
    path('', include(router.urls)),
]
