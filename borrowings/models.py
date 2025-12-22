from django.db import models
from django.conf import settings
from books.models import Book
from django.utils import timezone


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings"
    )

    def __str__(self):
        return f"Borrowing {self.id}: {self.user} borrowed {self.book} on {self.borrow_date}"

    def is_active(self):
        return self.actual_return_date is None

    def return_book(self):
        if self.actual_return_date is not None:
            raise ValueError("This borrowing has already been returned.")
        self.actual_return_date = timezone.now().date()
        self.save()

    def get_days(self):
        return (self.expected_return_date - self.borrow_date).days

    def get_total_price(self):
        return self.get_days() * self.book.daily_fee
