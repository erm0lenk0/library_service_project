from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from books.models import Book
from borrowings.models import Borrowing


User = get_user_model()


class BorrowingsAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="test@example.com",
            password="password123",
            first_name="User",
            last_name="Test",
            is_staff=False,
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

    def test_list_borrowings(self):
        url = reverse("borrowings-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_borrowing(self):
        url = reverse("borrowings-detail", args=[self.borrowing.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["book"]["title"], "Book Title")
        self.assertEqual(response.data["user"]["email"], "test@example.com")

    def test_create_borrowing(self):
        url = reverse("borrowings-list")
        data = {
            "borrow_date": "2025-02-01",
            "expected_return_date": "2025-02-10",
            "book": self.book.id,
            "user": self.user.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Borrowing.objects.count(), 2)

    def test_create_borrowing_invalid_data(self):
        url = reverse("borrowings-list")
        data = {
            "borrow_date": "2025-02-10",
            "expected_return_date": "2025-02-05",
            "book": self.book.id,
            "user": self.user.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("expected_return_date", response.data)
