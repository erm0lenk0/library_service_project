from django.urls import reverse
from rest_framework import viewsets, response
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment

User = get_user_model()


class PaymentsAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="payuser@example.com",
            password="password123",
            first_name="Pay",
            last_name="User",
            is_staff=False,
        )
        self.book = Book.objects.create(
            title="Payment Book",
            author="Author",
            cover="SOFT",
            inventory=3,
            daily_fee=2.00,
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date="2025-01-01",
            expected_return_date="2025-01-05",
        )
        self.payment = Payment.objects.create(
            borrowing=self.borrowing,
            money_to_pay=10.00,
            status="PENDING",
            type="PAYMENT",
        )
        self.client.force_authenticate(user=self.user)

    def test_list_payments(self):
        url = reverse("payments-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["borrowing"], self.borrowing.id)

    def test_retrieve_payments(self):
        url = reverse("payments-detail", args=[self.payment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["borrowing"], self.borrowing.id)
        self.assertEqual(response.data["status"], "PENDING")

    def test_payment_success_endpoint(self):
        url = reverse("payments-success")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Payment successful!", response.json()["message"])

    def test_payment_cancel_endpoint(self):
        url = reverse("payments-cancel")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Payment cancelled", response.json()["message"])
