from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView 
from base.utils import success_response, error_response
import razorpay
from django.conf import settings
from .razorpay_config import client
from rest_framework.permissions import AllowAny
from .models import Payment
from base.choices import PaymentStatus
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
import uuid
from based.models import UserProfile


class CheckoutAPIView(APIView):
    """
    This API endpoint creates a Razorpay order and returns the order details.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        amount = request.data.get("amount")
        userprofile = UserProfile.objects.get(id=1) # Replace with actual user retrieval logic
        user = userprofile.user

        if not amount:
            return error_response("Amount is required.")
        
        try:
            amount = int(amount)
            if amount <= 0:
                return error_response("Amount must be a positive number.")
        except (ValueError, TypeError):
            return error_response("Invalid amount provided.")

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        receipt_id = f"receipt_{uuid.uuid4().hex[:6]}"

        try:
            order = client.order.create(data={
                "amount": amount * 100,
                "currency": "INR",
                "receipt": receipt_id
            })
        except razorpay.errors.BadRequestError as e:
            return error_response(f"Razorpay Error: {str(e)}")

        Payment.objects.create(
            user=user,
            amount=amount,
            order_id=order.get('id'),
            status=PaymentStatus.CREATED
        )

        return success_response(order)


class PaymentStatusAPIView(APIView):
    """
    This API endpoint verifies the payment signature and updates the payment status.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': data['order_id'],
                'razorpay_payment_id': data['payment_id'],
                'razorpay_signature': data['signature']
            })
        except razorpay.errors.SignatureVerificationError:
            return error_response("Invalid signature")

        payment = Payment.objects.filter(order_id=data['order_id']).first()
        if payment:
            payment.status = PaymentStatus.PAID.value[0]
            payment.signiture = data['signature']
            payment.payment_id = data['payment_id']
            payment.save()

        return success_response("Payment verified and updated.")

from django.shortcuts import render

def razorpay_test_page(request):
    return render(request, "payment_test.html", context={"RAZORPAY_KEY_ID": settings.RAZORPAY_KEY_ID})


# @csrf_exempt
# def razorpay_webhook(request):
#     data = json.loads(request.body)
#     event = data.get("event")
#     payload = data.get("payload", {})

#     if event == "payment.captured":
#         payment_id = payload["payment"]["entity"]["id"]
#         order_id = payload["payment"]["entity"]["order_id"]
#         payment = Payment.objects.filter(order_id=order_id).first()
#         if payment:
#             payment.status = PaymentStatus.SUCCESS
#             payment.save()
    
#     return JsonResponse({"status": "ok"})
