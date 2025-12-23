import logging
from django.conf import settings
from payments.serializers import PaymentSerializer
from payments.services.stripe_service import create_checkout_session
from rest_framework import viewsets, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.response import Response
from notifications import send_telegram_message

from .filters import BorrowingFilter
from .models import Borrowing
from payments.models import Payment
from .serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer,
    BorrowingCreateResponseSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List all borrowings.",
        description=(
            "Return a list of borrowings for authenticated users.\n\n"
            "- Non-admin users see only their own borrowings.\n"
            "- Admin users can see all borrowings.\n"
            "- Supports filtering by `is_active` and `user` (admin only).\n\n"
            "Examples:\n"
            "`/api/borrowings/?is_active=true`\n"
            "`/api/borrowings/?user=5`"
        ),
        parameters=[
            OpenApiParameter(
                name="is_active",
                description="Filter borrowings by active status (true/false). Active means not yet returned.",
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name="user",
                description="Filter borrowings by user's ID (admin only).",
                required=False,
                type=int,
            ),
        ],
        responses={200: BorrowingSerializer},
        tags=["Borrowings"],
    ),
    retrieve=extend_schema(
        summary="Borrowing detail view.",
        description="Returns detailed information about a borrowing by ID.",
        responses={200: BorrowingSerializer},
        tags=["Borrowings"],
    ),
    create=extend_schema(
        summary="Create borrowing with payment",
        description=(
            "Creates a new borrowing record and automatically generates a Stripe payment session.\n\n"
            "Response includes:\n"
            "- Borrowing details\n"
            "- Payment object (status = PENDING)\n"
            "- Stripe checkout URL"
        ),
        responses={201: BorrowingCreateResponseSerializer},
        tags=["Borrowings"],
    ),
)
class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = BorrowingFilter

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingSerializer

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if not user.is_staff:
            qs = qs.filter(user=user)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = BorrowingCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        borrowing = serializer.save()

        session, payment = create_checkout_session(borrowing)

        response_data = {
            "borrowings": BorrowingSerializer(borrowing).data,
            "payments": PaymentSerializer(payment).data,
            "checkout_url": session.url,
        }

        return Response(
            BorrowingCreateResponseSerializer(response_data).data,
            status.status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Return borrowing.",
        description=(
            "Marks a borrowing as returned by setting `actual_return_date`.\n\n"
            "If the borrowing is already returned, an error is returned.\n"
            "If the book is overdue, a fine payment is created and returned in the response."
        ),
        responses={200: BorrowingSerializer},
        tags=["Borrowings"],
    )
    @action(detail=True, methods=["post"], url_path="return")
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()
        if borrowing.actual_return_date:
            return Response(
                {"error": "This borrowing is already returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        borrowing.return_book()

        fine_payment = None
        if borrowing.actual_return_date > borrowing.expected_return_date:
            days_overdue = (
                borrowing.actual_return_date - borrowing.expected_return_date
            ).days
            fine_amount = (
                days_overdue * borrowing.book.daily_fee * settings.FINE_MULTIPLIER
            )

            fine_payment = Payment.objects.create(
                borrowing=borrowing,
                money_to_pay=fine_amount,
                status="PENDING",
                type="FINE",
            )

        book_title = borrowing.book.title if borrowing.book else "Unknown"

        try:
            message = (
                f"Book returned!\n"
                f"User: {borrowing.user.username}\n"
                f"Book: {book_title}\n"
                f"Return date: {borrowing.actual_return_date}"
            )
            response_data = {"borrowings": BorrowingSerializer(borrowing).data}
            if fine_payment:
                message += f"\nOverdue! Fine created: ${fine_payment.money_to_pay}"
                response_data["fine_payment"] = PaymentSerializer(fine_payment).data
            send_telegram_message(message)
        except Exception as e:
            logging.error(f"Error sending return notification: {e}")

        response_data = {"borrowing": BorrowingSerializer(borrowing).data}
        if fine_payment:
            response_data["fine_payment"] = PaymentSerializer(fine_payment).data

        return Response(response_data, status=status.HTTP_200_OK)
