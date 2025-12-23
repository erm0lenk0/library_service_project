from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from borrowings.models import Borrowing
from books.models import Book
from users.models import User


class BorrowingsFilteringAPITest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass",
            first_name="Admin",
            last_name="User",
        )
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            password="password123",
            first_name="User",
            last_name="One",
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            password="password123",
            first_name="User",
            last_name="Two",
        )

        self.book = Book.objects.create(
            title="Book Title",
            author="Author",
            cover="SOFT",
            inventory=5,
            daily_fee=1.5,
        )

        self.borrowing1 = Borrowing.objects.create(
            user=self.user1,
            book=self.book,
            borrow_date="2025-01-01",
            expected_return_date="2025-01-10",
            actual_return_date=None,
        )
        self.borrowing2 = Borrowing.objects.create(
            user=self.user1,
            book=self.book,
            borrow_date="2025-01-02",
            expected_return_date="2025-01-12",
            actual_return_date="2025-01-05",
        )
        self.borrowing3 = Borrowing.objects.create(
            user=self.user2,
            book=self.book,
            borrow_date="2025-01-03",
            expected_return_date="2025-01-15",
            actual_return_date=None,
        )

    def test_user_sees_only_own_borrowings(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("borrowings-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [b["id"] for b in response.data]
        self.assertEqual(set(ids), {self.borrowing1.id, self.borrowing2.id})

    def test_filter_is_active(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("borrowings-list")
        response = self.client.get(url, {"is_active": "True"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [b["id"] for b in response.data]
        self.assertEqual(set(ids), {self.borrowing1.id})

    def test_admin_can_filter_by_user(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("borrowings-list")
        response = self.client.get(url, {"user": self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [b["id"] for b in response.data]
        self.assertEqual(set(ids), {self.borrowing3.id})

    def test_unauthenticated_user_cannot_access(self):
        url = reverse("borrowings-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
