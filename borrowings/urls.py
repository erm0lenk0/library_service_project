from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import BorrowingViewSet


router = DefaultRouter()
router.register(r"borrowings", BorrowingViewSet, basename="borrowings")


urlpatterns = router.urls
