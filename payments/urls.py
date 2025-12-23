from django.urls import path
from .api.stripe_webhook import stripe_webhook
from .views import payment_success, payment_cancel, PaymentListView, PaymentDetailView

urlpatterns = [
    path("stripe/webhook/", stripe_webhook, name="stripe-webhook"),
    path("payments/success/", payment_success, name="payments-success"),
    path("payments/cancel/", payment_cancel, name="payments-cancel"),
    path("payments/", PaymentListView.as_view(), name="payments-list"),
    path("payments/<int:pk>/", PaymentDetailView.as_view(), name="payments-detail"),
]
