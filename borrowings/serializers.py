from rest_framework import serializers
from .models import Borrowing
from books.serializers import BookSerializer
from users.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "is_active",
        ]

    def get_is_active(self, obj):
        return obj.is_active()


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "borrow_date",
            "expected_return_date",
            "book",
        ]

    def validate(self, data):
        borrow_date = data.get("borrow_date")
        expected_return_date = data.get("expected_return_date")

        if expected_return_date <= borrow_date:
            raise serializers.ValidationError(
                {
                    "expected_return_date": "The return date must be later than the issue date."
                }
            )
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        borrowing = Borrowing.objects.create(user=user, **validated_data)
        return borrowing


class BorrowingReturnsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ["id", "actual_return_date"]
        read_only_fields = ["id", "actual_return_date"]
