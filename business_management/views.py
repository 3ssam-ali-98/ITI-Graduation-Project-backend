from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, filters, status, generics
from rest_framework.decorators import api_view
# from django.shortcuts import render
from rest_framework import viewsets, filters
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from business_management.models import Business, Task, User, Client
from business_management.serializers import BusinessSerializer, TaskSerializer, UserSerializer, ClientSerializer
from business_management.filters import BusinessFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import update_last_login
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from rest_framework.authentication import TokenAuthentication
from django.views import View
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Count, Q, F
import paypalrestsdk
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from urllib.parse import parse_qs
from paypalrestsdk import Payment


paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})


class EmployeeTaskPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.user_type == 'Employee' and
            request.method in ['GET', 'PATCH']
        )

    def has_object_permission(self, request, view, obj):
        if request.method == 'PATCH':
            if obj.assigned_to != request.user:
                raise PermissionDenied("You can only modify tasks assigned to you.")
            allowed_fields = {'completed'}
            requested_fields = set(request.data.keys())
            if not requested_fields.issubset(allowed_fields):
                raise PermissionDenied("You can only modify the 'completed' field.")
        return True

class TaskViewSet(viewsets.ModelViewSet):
	serializer_class = TaskSerializer
	permission_classes = [IsAuthenticated, EmployeeTaskPermission]

	def get_queryset(self):
			user = self.request.user
			return Task.objects.filter(business=user.business)

	def perform_create(self, serializer):
			owner = self.request.user
			task = serializer.save(business=owner.business)
			task.save()
	def update(self, request, *args, **kwargs):
		"""Handles PUT requests (full update)"""
		instance = self.get_object()
		previous_completed_status = instance.completed  
		super().update(request, *args, **kwargs)  


		instance.refresh_from_db()
		if not previous_completed_status and instance.completed:  
			instance.completed_by = request.user
			instance.completed_at = now()
			instance.save()

		serializer = self.get_serializer(instance)
		return Response(serializer.data, status=status.HTTP_200_OK)

	def partial_update(self, request, *args, **kwargs):
		"""Handles PATCH requests (partial update)"""
		instance = self.get_object()
		previous_completed_status = instance.completed  
		response = super().partial_update(request, *args, **kwargs)  


		instance.refresh_from_db()
		if not previous_completed_status and instance.completed:
			instance.completed_by = request.user
			instance.completed_at = now()
			instance.save()

		return response


# class TaskViewSet(viewsets.ModelViewSet):
#     serializer_class = TaskSerializer

#     def get_queryset(self):
#         business_id = self.kwargs.get('business_id')
#         return Tasks.objects.filter(business__id=business_id)


class EmployeeCanReadAndCreateOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.user_type == "Employee":
            return request.method in ["GET", "POST"]

        return True

class ClientViewSet(viewsets.ModelViewSet):
	serializer_class = ClientSerializer
	permission_classes = [IsAuthenticated, EmployeeCanReadAndCreateOnly]

	def get_queryset(self):
		user = self.request.user

		return Client.objects.filter(business=user.business)

	def perform_create(self, serializer):
		owner = self.request.user
		client = serializer.save(business=owner.business)
		client.save()



class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.user_type != "Employee"

class EmployeeViewSet(viewsets.ModelViewSet):
	serializer_class = UserSerializer
	permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

	def get_queryset(self):
		user = self.request.user 
		return User.objects.filter(user_type="Employee", business=user.business)

	def perform_create(self, serializer):
		owner = self.request.user
		user = serializer.save()
		user.business = owner.business 
		user.save()


class UserListCreateView(generics.ListCreateAPIView):
	queryset = User.objects.filter(is_superuser=False, is_staff=False)
	serializer_class = UserSerializer
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = ['user_type']
	search_fields = ['username']

	def perform_create(self, serializer):
		user = serializer.save()
		business = Business.objects.create(name=self.request.data.get("business_name"), owner=user)
		user.business = business
		user.save()


class UserDetailView(APIView):
	def get(self, request, pk):
		user = get_object_or_404(User, pk=pk)
		serializer = UserSerializer(user)
		return Response(serializer.data)

	def put(self, request, pk):
		user = get_object_or_404(User, pk=pk)
		data = request.data.copy()
		data.pop("is_superuser", None)
		data.pop("is_staff", None)
		data.pop("email", None)	

		if "password" in data:
			data["password"] = make_password(data["password"])

		if "business_name" in data:
			if user.business:
				user.business.name = data["business_name"]
				user.business.save()
		
		serializer = UserSerializer(user, data=data)
  
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def patch(self, request, pk):
		user = get_object_or_404(User, pk=pk)
		data = request.data.copy()
		data.pop("is_superuser", None)
		data.pop("is_staff", None)
		data.pop("email", None)
  
		if "password" in data:
			data["password"] = make_password(data["password"])
   
		if "business_name" in data:
			if user.business:
				user.business.name = data["business_name"]
				user.business.save()
    
		serializer = UserSerializer(user, data=data, partial=True)
  
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk):
		user = get_object_or_404(User, pk=pk)
		user.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)


class BusinessView(viewsets.ModelViewSet):
	queryset = Business.objects.all()
	serializer_class = BusinessSerializer   
	filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
	filterset_class = BusinessFilter
	search_fields = ["name", "owner"]
	ordering_fields = ["name", "created_at"] 


class LoginView(APIView):
	def post(self, request):
		email = request.data.get("email")
		password = request.data.get("password")

		try:
			user = User.objects.get(email=email)  
			if user.check_password(password):  

				refresh = RefreshToken.for_user(user)
				return Response({"token": str(refresh.access_token), "refresh_token": str(refresh), "user_id": user.id , "user_type": user.user_type, "user_name": user.first_name, "is_premuim":user.business.is_premium}, status=status.HTTP_200_OK)
				# token, created = Token.objects.get_or_create(user=user)
				# return Response({"token": token.key, "user_id": user.id , "user_type": user.user_type, "user_name": user.first_name}, status=status.HTTP_200_OK)
		except User.DoesNotExist:
			pass

		return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def validate_password(request):
    user = request.user
    password = request.data.get("password")

    if user.check_password(password):
        return Response({"valid": True}, status=status.HTTP_200_OK)
    return Response({"valid": False}, status=status.HTTP_400_BAD_REQUEST)

class TaskAnalytics(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		user = request.user
		if not user.business.is_premium:
			return JsonResponse({'error': 'Analytics is available only for premium businesses'}, status=403)

		today = now().replace(hour=0, minute=0, second=0, microsecond=0)
		first_day_of_month = today.replace(day=1)
		first_day_last_month = (first_day_of_month - timedelta(days=1)).replace(day=1)

		tasks_created_this_month = Task.objects.filter(
			business=user.business,
			created_at__gte=first_day_of_month
		).count()
		tasks_created_last_month = Task.objects.filter(
			business=user.business,
			created_at__gte=first_day_last_month,
			created_at__lt=first_day_of_month
		).count()
		created_prcentage_change = calculate_percentage(tasks_created_last_month, tasks_created_this_month)

		tasks_completed_this_month = Task.objects.filter(
			business=user.business,
			completed=True,
			completed_at__gte=first_day_of_month
		)
		tasks_completed_this_month_count = tasks_completed_this_month.count()
  
		tasks_completed_last_month = Task.objects.filter(
			business=user.business,
			completed=True,
			completed_at__gte=first_day_last_month,
			completed_at__lt=first_day_of_month
		)
		tasks_completed_last_month_count = tasks_completed_last_month.count()

		completed_prcentage_change = calculate_percentage(tasks_completed_last_month_count, tasks_completed_this_month_count)
  
		tasks_completed_within_deadline_this_month = tasks_completed_this_month.filter(completed_at__lte=F('deadline')).count()
		tasks_completed_within_deadline_last_month = tasks_completed_last_month.filter(completed_at__lte=F('deadline')).count()
		completed_within_deadline_percentage_change = calculate_percentage(tasks_completed_within_deadline_last_month, tasks_completed_within_deadline_this_month)
	
		tasks_completed_outside_deadline_this_month = tasks_completed_this_month.filter(completed_at__gt=F('deadline')).count()
		tasks_completed_outside_deadline_last_month = tasks_completed_last_month.filter(completed_at__gt=F('deadline')).count()
		completed_outside_deadline_percentage_change = calculate_percentage(tasks_completed_outside_deadline_last_month, tasks_completed_outside_deadline_this_month)
  
		top_employee_completed = User.objects.filter(business=user.business, completed_tasks__completed_at__gte=first_day_of_month).annotate(task_count=Count('completed_tasks')).order_by('-task_count').first()
		top_employee_assigned = User.objects.filter(business=user.business, tasks__created_at__gte=first_day_of_month).annotate(task_count=Count('tasks')).order_by('-task_count').first()
  
		employee_with_most_tasks = User.objects.filter(business=user.business, tasks__completed=False).annotate(task_count=Count('tasks')).order_by('-task_count').first()

		notcompleted_tasks =Task.objects.filter(
			business=user.business,
			completed=False,
		).values('name', 'deadline', 'assigned_to__username')
  
		tasks_overdue = Task.objects.filter(
			business=user.business,
			completed=False,
			deadline__lt=today
		).values('name', 'deadline', 'assigned_to__username')
  
		return JsonResponse({
        'tasks_created_this_month': tasks_created_this_month,
        'created_tasks_percentage_change': created_prcentage_change,
        'tasks_completed_this_month': tasks_completed_this_month_count,
        'completed_tasks_percentage_change': completed_prcentage_change,
        'completed_within_deadline': tasks_completed_within_deadline_this_month,
        'completed_within_deadline_percentage_change': completed_within_deadline_percentage_change,
        'completed_after_deadline': tasks_completed_outside_deadline_this_month,
        'completed_after_deadline_percentage_change': completed_outside_deadline_percentage_change,
        'top_employee_completed': top_employee_completed.username if top_employee_completed else None,
        'top_employee_assigned': top_employee_assigned.username if top_employee_assigned else None,
        'top_employee_uncompleted': employee_with_most_tasks.username if employee_with_most_tasks else None,
        'notcompleted_tasks': list(notcompleted_tasks),
        'overdue_tasks': list(tasks_overdue),
    })


def calculate_percentage(prev, current):
	if prev == 0:
		return "100.00% increase" if current > 0 else "No change"
	if prev == current:
		return "No change"
	elif prev < current:
		prcent = (current - prev) / prev * 100
		return f"{prcent:.2f}% increase"
	elif prev > current:
		prcent = (prev - current) / prev * 100
		return f"{prcent:.2f}% decrease"


class PaymentView(APIView):
	permission_classes = [IsAuthenticated]
	def post(self, request):
		user_id = request.user.id  

		payment = paypalrestsdk.Payment({
			"intent": "sale",
			"payer": {
				"payment_method": "paypal"
			},
			"redirect_urls": {
				"return_url": f"http://localhost:8000/execute-payment/?user_id={user_id}",  
				"cancel_url": "http://localhost:8000/payment-cancelled/"
			},
			"transactions": [{
				"amount": {
					"total": "10.00",
					"currency": "USD"
				},
				"description": "upgrade membership to premium"
			}]
		})

		if payment.create():
			for link in payment.links:
				if link.rel == "approval_url":
					return JsonResponse({"approval_url": link.href})
		else:
			return JsonResponse({"error": payment.error}, status=400)


def execute_payment(request):
	payment_id = request.GET.get("paymentId")
	payer_id = request.GET.get("PayerID")
	user_id = request.GET.get("user_id")

	if not payment_id or not payer_id or not user_id:
		return JsonResponse({"error": "Missing payment details"}, status=400)

	try:
		payment = Payment.find(payment_id)
	except paypalrestsdk.exceptions.PayPalConnectionError as e:
		return JsonResponse({"error": f"PayPal connection error: {str(e)}"}, status=500)
	except Exception as e:
		return JsonResponse({"error": f"Error finding payment: {str(e)}"}, status=500)

	if payment.execute({"payer_id": payer_id}):
		user = User.objects.get(id=user_id)
		business = user.business
		business.is_premium = True
		business.save()
		return JsonResponse({"message": "Payment successful, business upgraded."})
	else:
		print(f"PayPal error: {payment.error}")
		return JsonResponse({"error": payment.error}, status=500)
