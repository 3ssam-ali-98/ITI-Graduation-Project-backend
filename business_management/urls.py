from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'business', BusinessView, basename='business')

urlpatterns = [
    path('', include(router.urls)),
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
	path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('login/', LoginView.as_view(), name='login'),
]
