from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema_view, extend_schema

from .models import Book
from books.serializers import BookSerializer
from .permissions import IsAdminOrReadOnly


@extend_schema_view(
    list=extend_schema(
        summary="List all books",
        description="Returns a list of all books. Requires authentication.",
        responses={200: BookSerializer},
        tags=["Books"],
    ),
    retrieve=extend_schema(
        summary="Book detail view",
        description="Returns detailed information about a book by ID.",
        responses={200: BookSerializer},
        tags=["Books"],
    ),
    create=extend_schema(
        summary="Create a new book",
        description="Creates a new book. Only available to administrators.",
        request=BookSerializer,
        responses={201: BookSerializer},
        tags=["Books"],
    ),
    update=extend_schema(
        summary="Update a book",
        description="Updates a book. Only available to administrators.",
        request=BookSerializer,
        responses={200: BookSerializer},
        tags=["Books"],
    ),
    partial_update=extend_schema(
        summary="Partial update a book",
        description="Partially updates book data. Only available to administrators.",
        request=BookSerializer,
        responses={200: BookSerializer},
        tags=["Books"],
    ),
    destroy=extend_schema(
        summary="Delete book",
        description="Deletes a book. Only available to administrators.",
        responses={204: None},
        tags=["Books"],
    )
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
