from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from borrowings.models import Borrowing
from books.models import Book
from django.utils import timezone

User = get_user_model()


class BorrowingsReturnAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            first_name="User",
            last_name="Test",
        )
        self.book = Book.objects.create(
            title="Book Title",
            author="Author",
            cover="SOFT",
            inventory=5,
            daily_fee=1.50,
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date="2025-01-01",
            expected_return_date="2025-01-10",
        )
        self.client.force_authenticate(user=self.user)

    def test_return_borrowing_success(self):
        url = reverse("borrowings-return-borrowing", args=[self.borrowing.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.borrowing.refresh_from_db()
        self.assertIsNotNone(self.borrowing.actual_return_date)

    def test_return_borrowing_twice(self):
        self.borrowing.actual_return_date = timezone.now().date()
        self.borrowing.save()

        url = reverse("borrowings-return-borrowing", args=[self.borrowing.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
