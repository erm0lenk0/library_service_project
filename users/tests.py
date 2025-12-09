from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse

User = get_user_model()


class UserAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password",
            first_name="User",
            last_name="Test",
            is_staff=False,
        )
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="password",
            first_name="Admin",
            last_name="Test",
            is_staff=True,
        )

    def test_list_users_requires_authentication(self):
        url = reverse("users-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_register(self):
        url = reverse("users-list")
        payload = {
            "email": "new@example.com",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    def test_user_can_view_own_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("users-detail", args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_admin_can_delete_user(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("users-detail", args=[self.user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_user_cannot_delete_other_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("users-detail", args=[self.admin.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

