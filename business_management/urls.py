from django.urls import path, include
from rest_framework.routers import DefaultRouter
from business_management.views import BusinessView

router = DefaultRouter()
router.register(r'business', BusinessView, basename='business')

urlpatterns = [
    path('', include(router.urls)),
]