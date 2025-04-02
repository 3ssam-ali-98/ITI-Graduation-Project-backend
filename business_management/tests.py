from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import *
from .views import *
from .views import EmployeeCanReadAndCreateOnly


class ClientTest(TestCase):
	def setUp(self):
		self.business = Business.objects.create(name='Test Business')
		self.test_instance = Client.objects.create(
			name='Test Name',
			email='test@email.com',
			phone='0123456789',
			address='Test Address',
			notes='Test Notes',
			business=self.business
		)

	def test_model_creation(self):
		self.assertEqual(Client.objects.count(), 1)
		self.assertEqual(self.test_instance.name, "Test Name")
		self.assertEqual(self.test_instance.phone, "0123456789")

	def test_model_string_representation(self):
		self.assertEqual(str(self.test_instance), "Test Name")


class BusinessTest(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='testuser', password='testpassword')
		self.test_instance = Business.objects.create(
			name='Test Business',
			owner=self.user
		)

	def test_model_creation(self):
		self.assertEqual(Business.objects.count(), 1)
		self.assertEqual(self.test_instance.name, "Test Business")
		self.assertEqual(self.test_instance.owner, self.user)

	def test_model_string_representation(self):
		self.assertEqual(str(self.test_instance), "Test Business")


class TaskTest(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='testuser', password='testpassword')
		self.business = Business.objects.create(name='Test Business', owner=self.user)
		self.test_instance = Task.objects.create(
			name="Test Task",
			description="This is a test task.",
			priority="High",
			deadline=now() + timedelta(days=7),
			completed=False,
			business=self.business,
			assigned_to=self.user
		)

	def test_model_creation(self):
		self.assertEqual(Task.objects.count(), 1)
		self.assertEqual(self.test_instance.name, "Test Task")
		self.assertEqual(self.test_instance.priority, "High")
		self.assertEqual(self.test_instance.completed, False)
		self.assertEqual(self.test_instance.business, self.business)
		self.assertEqual(self.test_instance.assigned_to, self.user)

	def test_model_string_representation(self):
		self.assertEqual(str(self.test_instance), "Test Task")


class UserTest(TestCase):
	def setUp(self):
		self.business = Business.objects.create(name='Test Business')
		self.test_instance = User.objects.create_user(
			first_name="John",
			last_name="Doe",
			username="johndoe",
			user_type="Business Owner",
			email="johndoe@example.com",
			mobile_phone="01234567890",
			business=self.business
		)

	def test_model_creation(self):
		self.assertEqual(User.objects.count(), 1)
		self.assertEqual(self.test_instance.first_name, "John")
		self.assertEqual(self.test_instance.last_name, "Doe")
		self.assertEqual(self.test_instance.username, "johndoe")
		self.assertEqual(self.test_instance.user_type, "Business Owner")
		self.assertEqual(self.test_instance.email, "johndoe@example.com")
		self.assertEqual(self.test_instance.mobile_phone, "01234567890")
		self.assertEqual(self.test_instance.business, self.business)

	def test_model_string_representation(self):
		self.assertEqual(str(self.test_instance), "John Doe - johndoe")


class TaskViewSetTest(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='testuser', password='testpassword')
		self.business = Business.objects.create(name='Test Business', owner=self.user)
		self.client.force_authenticate(user=self.user)
		self.task = Task.objects.create(
			name="Test Task",
			description="This is a test task.",
			priority="High",
			deadline=now() + timedelta(days=7),
			completed=False,
			business=self.business,
			assigned_to=self.user
		)
		self.url = reverse('task-list')

	def test_get_queryset(self):
		response = self.client.get(self.url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]['name'], "Test Task")

	def test_create_task(self):
		data = {
			"name": "New Task",
			"description": "This is a new task.",
			"priority": "Medium",
			"deadline": (now() + timedelta(days=5)).isoformat(),
			"completed": False,
			"assigned_to": self.user.id
		}
		response = self.client.post(self.url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Task.objects.count(), 2)
		self.assertEqual(Task.objects.last().name, "New Task")
		self.assertEqual(Task.objects.last().business, self.business)

	def test_permission_denied_for_unauthenticated_user(self):
		self.client.force_authenticate(user=None)
		response = self.client.get(self.url)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_authenticated_user_access(self):
		response = self.client.get(self.url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]['name'], "Test Task")


class MockView(APIView):
	permission_classes = [EmployeeCanReadAndCreateOnly]

	def get(self, request):
		return Response({"message": "GET request successful"}, status=status.HTTP_200_OK)

	def post(self, request):
		return Response({"message": "POST request successful"}, status=status.HTTP_201_CREATED)

	def delete(self, request):
		return Response({"message": "DELETE request successful"}, status=status.HTTP_204_NO_CONTENT)


class EmployeeCanReadAndCreateOnlyTest(TestCase):
	def setUp(self):
		self.factory = APIRequestFactory()
		self.business = Business.objects.create(name="Test Business")
		self.employee_user = User.objects.create_user(
			username="employee",
			password="password",
			user_type="Employee",
			business=self.business,
		)
		self.owner_user = User.objects.create_user(
			username="owner",
			password="password",
			user_type="Business Owner",
			business=self.business,
		)

	def test_employee_can_get(self):
		request = self.factory.get("/mock/")
		force_authenticate(request, user=self.employee_user)
		response = MockView.as_view()(request)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_employee_can_post(self):
		request = self.factory.post("/mock/", {"data": "test"})
		force_authenticate(request, user=self.employee_user)
		response = MockView.as_view()(request)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_employee_cannot_delete(self):
		request = self.factory.delete("/mock/")
		force_authenticate(request, user=self.employee_user)
		response = MockView.as_view()(request)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_owner_can_access_all_methods(self):
		request = self.factory.get("/mock/")
		force_authenticate(request, user=self.owner_user)
		response = MockView.as_view()(request)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		request = self.factory.post("/mock/", {"data": "test"})
		force_authenticate(request, user=self.owner_user)
		response = MockView.as_view()(request)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		request = self.factory.delete("/mock/")
		force_authenticate(request, user=self.owner_user)
		response = MockView.as_view()(request)
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

	def test_unauthenticated_user_cannot_access(self):
		request = self.factory.get("/mock/")
		response = MockView.as_view()(request)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserListCreateViewTest(APITestCase):
	def setUp(self):
		self.owner_user = User.objects.create_user(
			username="owner",
			password="password",
			user_type="Business Owner",
			email="owner@example.com"
		)
		self.client.force_authenticate(user=self.owner_user)
		self.url = reverse('user-list-create')

	def test_list_users(self):
		response = self.client.get(self.url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)

	def test_create_user_with_business(self):
		data = {
			"username": "newuser",
			"password": "newpassword",
			"user_type": "Employee",
			"email": "newuser@example.com",
			"business_name": "New Business"
		}
		response = self.client.post(self.url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(User.objects.count(), 2)
		new_user = User.objects.get(username="newuser")
		self.assertEqual(new_user.business.name, "New Business")


class UserDetailViewTest(APITestCase):
	def setUp(self):
		self.owner_user = User.objects.create_user(
			username="owner",
			password="password",
			user_type="Business Owner",
			email="owner@example.com"
		)
		self.business = Business.objects.create(name="Test Business", owner=self.owner_user)
		self.owner_user.business = self.business
		self.owner_user.save()
		self.employee_user = User.objects.create_user(
			username="employee",
			password="password",
			user_type="Employee",
			email="employee@example.com",
			business=self.business
		)
		self.client.force_authenticate(user=self.owner_user)
		self.url = reverse('user-detail', kwargs={'pk': self.employee_user.pk})

	def test_get_user_detail(self):
		response = self.client.get(self.url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['username'], "employee")

	def test_update_user(self):
		data = {
			"username": "updatedemployee",
			"password": "newpassword",
			"business_name": "Updated Business"
		}
		response = self.client.put(self.url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		updated_user = User.objects.get(pk=self.employee_user.pk)
		self.assertEqual(updated_user.username, "updatedemployee")
		self.assertEqual(updated_user.business.name, "Updated Business")

	def test_partial_update_user(self):
		data = {
			"username": "partiallyupdatedemployee"
		}
		response = self.client.patch(self.url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		updated_user = User.objects.get(pk=self.employee_user.pk)
		self.assertEqual(updated_user.username, "partiallyupdatedemployee")

	def test_delete_user(self):
		response = self.client.delete(self.url)
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(User.objects.filter(pk=self.employee_user.pk).exists())
