from django.http import JsonResponse
from rest_framework import permissions, generics
from payments.models import Payment
from payments.serializers import PaymentSerializer


def payment_success(request):
    return JsonResponse({"message": "Payment successful!"})


def payment_cancel(request):
    return JsonResponse({"message": "Payment cancelled, you can retry within 24h."})


class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(borrowing__user=user)


class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(borrowing__user=user)
