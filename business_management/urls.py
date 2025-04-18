from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'business', BusinessView, basename='business')
router.register(r'admin-tasks', AdminTaskViewSet, basename='admin-tasks')
router.register(r'admin-users', AdminUserViewSet, basename='admin-users')
router.register(r'admin-clients', AdminClientViewSet, basename='admin-clients')


urlpatterns = [
    path('', include(router.urls)),
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
	path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
	path('businessdetail/<int:pk>/', BusinessDetailView.as_view(), name='business-detail'),
    path('login/', LoginView.as_view(), name='login'),
    path('validate-password/', validate_password, name='validate-password'),
    path('tasks-analytics/', TaskAnalytics.as_view(), name='tasks-analytics'),
    path('payment/', PaymentView.as_view(), name='payment'),
    # path('paypal/', include('paypal.standard.ipn.urls')),
    path('execute-payment/', execute_payment, name='execute-payment'),
    path('custom-admin-login/', AdminLoginView.as_view(), name='admin-login'),
]
