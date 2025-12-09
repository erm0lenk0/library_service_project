from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model

from .serializers import UserSerializer, UserCreateSerializer, UserDetailSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permissions_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action == "retrieve":
            return UserDetailSerializer
        return UserSerializer
