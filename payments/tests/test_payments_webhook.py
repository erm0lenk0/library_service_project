import json

import stripe
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment
from unittest.mock import patch

User = get_user_model()


class StripeWebhookTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="webhook@example.com",
            password="password123",
            first_name="Hook",
            last_name="Test",
            is_staff=False,
        )
        self.book = Book.objects.create(
            title="Webhook Book",
            author="Author",
            cover="SOFT",
            inventory=2,
            daily_fee=3.00,
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date="2025-02-01",
            expected_return_date="2025-01-10",
        )
        self.payment = Payment.objects.create(
            borrowing=self.borrowing,
            money_to_pay=15.00,
            status="PENDING",
            type="PAYMENT",
            session_id="fake_session_id",
        )

    @patch("payments.api.stripe_webhook.stripe.Webhook.construct_event")
    def test_webhook_checkout_session_completed(self, mock_construct_event):
        url = reverse("stripe-webhook")

        mock_construct_event.return_value = {
            "type": "checkout.session.completed",
            "data": {"object": {"id": "fake_session_id"}},
        }

        response = self.client.post(
            url,
            data=json.dumps({"id": "evt_test_webhook"}),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_signature",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "PAID")
