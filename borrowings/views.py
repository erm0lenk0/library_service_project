from rest_framework import viewsets, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import BorrowingFilter
from .models import Borrowing
from .serializers import BorrowingSerializer, BorrowingCreateSerializer


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
        summary="Create borrowing.",
        description="Creates a new borrowing record. Requires authentication.",
        responses={201: BorrowingCreateSerializer},
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

    @extend_schema(
        summary="Return borrowing.",
        description=(
            "Marks a borrowing as returned by setting `actual_return_date`.\n\n"
            "If the borrowing is already returned, an error is returned."
        ),
        responses={200: BorrowingSerializer},
        tags=["Borrowings"],
    )
    @action(detail=True, methods=["post"], url_path="return")
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()
        try:
            borrowing.return_book()
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = BorrowingSerializer(borrowing)
        return Response(serializer.data)
