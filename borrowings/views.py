from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema_view, extend_schema

from .models import Borrowing
from .serializers import BorrowingSerializer, BorrowingCreateSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List all borrowings.",
        description="Return a list of all borrowings for authenticated users.",
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

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingSerializer
