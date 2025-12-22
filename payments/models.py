from django.db import models
from borrowings.models import Borrowing


class Payment(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("CANCELLED", "CancelLed"),
    ]
    TYPE_CHOICES = [
        ("PAYMENT", "Payment"),
        ("FINE", "Fine"),
    ]

    borrowing = models.ForeignKey(
        Borrowing,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="PAYMENT")
    session_url = models.URLField(
        blank=True,
        null=True,
    )
    session_id = models.CharField(max_length=255, blank=True, null=True)
    money_to_pay = models.DecimalField(
        decimal_places=2,
        max_digits=10,
    )

    def __str__(self):
        return f"Payment {self.id} for Borrowing {self.borrowing.id} ({self.status})"
