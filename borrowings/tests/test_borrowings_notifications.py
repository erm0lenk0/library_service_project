from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from borrowings.models import Borrowing
from books.models import Book
from unittest.mock import patch

User = get_user_model()


class BorrowingsNotificationsAPITest(APITestCase):
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
        self.client.force_authenticate(user=self.user)

    @patch("borrowings.serializers.send_telegram_message")
    def test_create_borrowing_sends_notification(self, mock_send):
        url = reverse("borrowings-list")
        payload = {
            "borrow_date": "2025-01-01",
            "expected_return_date": "2025-01-10",
            "book": self.book.id,
        }
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        borrowing = Borrowing.objects.get()
        self.assertEqual(borrowing.user, self.user)

        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        self.assertIn("New rental!", args[0])

    @patch("borrowings.views.send_telegram_message")
    def test_return_borrowing_sends_notification(self, mock_send):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date="2025-01-01",
            expected_return_date="2025-01-10",
        )
        url = reverse("borrowings-return-borrowing", args=[borrowing.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        borrowing.refresh_from_db()
        self.assertIsNotNone(borrowing.actual_return_date)

        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        self.assertIn("Book returned", args[0])
