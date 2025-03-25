from django.urls import path, include
from rest_framework.routers import DefaultRouter
from business_management.views import BusinessView
from .views import EmployeeViewSet, LoginView, TaskViewSet, validate_password
from .views import ClientViewSet
from .views import UserListCreateView, UserDetailView



router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'business', BusinessView, basename='business')

# router.register(r'business/(?P<business_id>\d+)/tasks', TaskViewSet, basename='tasks')

urlpatterns = [
    path('', include(router.urls)),
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
	path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('login/', LoginView.as_view(), name='login'),
    path('validate-password/', validate_password, name='validate-password'),
]

