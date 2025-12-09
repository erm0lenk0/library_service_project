from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_view, extend_schema

from .serializers import UserSerializer, UserCreateSerializer, UserDetailSerializer

User = get_user_model()

@extend_schema_view(
    list=extend_schema(
        summary="List all users",
        description="Returns a list of all users (authorization required).",
        responses={200: UserSerializer},
        tags=["Users"],
    ),
    retrieve=extend_schema(
        summary="User detail view",
        description="Returns detailed information about the user by ID.",
        responses={200: UserDetailSerializer},
        tags=["Users"],
    ),
    create=extend_schema(
        summary="New user registration",
        description="Creates a new user. Available without authorization.",
        request=UserCreateSerializer,
        responses={201: UserDetailSerializer},
        tags=["Users"],
    ),
    update=extend_schema(
        summary="Updated user",
        description="Updates user data (authorization required).",
        request=UserSerializer,
        responses={200: UserSerializer},
        tags=["Users"],
    ),
    partial_update=extend_schema(
        summary="Partial updated user",
        description="Partially updates user data (authorization required).",
        request=UserSerializer,
        responses={200: UserSerializer},
        tags=["Users"],
    ),
    destroy=extend_schema(
        summary="Destroy user",
        description="Deletes a user. Only available to administrator.",
        responses={204: None},
        tags=["Users"],
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]

        elif self.action == "destroy":
            return [permissions.IsAdminUser()]

        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action == "retrieve":
            return UserDetailSerializer
        return UserSerializer
