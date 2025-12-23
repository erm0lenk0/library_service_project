import stripe
from django.conf import settings
from payments.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(borrowing):
    total_price = borrowing.total_price()

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": borrowing.book.title},
                    "unit_amount": int(total_price * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="http://localhost:8000/api/payments/success",
        cancel_url="http://localhost:8000/api/payments/cancel",
    )

    payment = Payment.objects.create(
        borrowing=borrowing,
        money_to_pay=total_price,
        session_url=session.url,
        session_id=session.id,
        status="PENDING",
        type="PAYMENT",
    )

    return session, payment
