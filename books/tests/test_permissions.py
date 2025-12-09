from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from books.models import Book

class BookPermissionTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="user", password="password", is_staff=False
        )
        self.admin = User.objects.create_user(
            username="admin", password="password", is_staff=True
        )
        self.book = Book.objects.create(
            title="Test Book", author="Author", cover="SOFT", inventory=5, daily_fee=1.50
        )

    def test_list_books_requires_authentication(self):
        response = self.client.get("/api/books/")
        self.assertEqual(response.status_code, 401)

        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/books/")
        self.assertEqual(response.status_code, 200)

    def test_user_cannot_create_book(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/books/", {
            "title": "New Book",
            "author": "Author",
            "cover": "SOFT",
            "inventory": 3,
            "daily_fee": 1.50
        })
        self.assertEqual(response.status_code, 403)

    def test_admin_can_create_book(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/api/books/", {
            "title": "Admin Book",
            "author": "Admin Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": 2.00
        })
        self.assertEqual(response.status_code, 201)

    def test_user_cannot_delete_book(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/books/{self.book.id}/")
        self.assertEqual(response.status_code, 403)

    def test_admin_can_delete_book(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f"/api/books/{self.book.id}/")
        self.assertEqual(response.status_code, 204)