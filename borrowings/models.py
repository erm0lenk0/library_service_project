from django.db import models
from django.conf import settings
from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrower")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrower"
    )

    def __str__(self):
        return f"Borrowing {self.id}: {self.user} borrowed {self.book} on {self.borrow_date}"
