from django.urls import path, include, re_path
from .views import CheckoutAPIView, PaymentStatusAPIView, razorpay_test_page

urlpatterns = [
    path('checkout', CheckoutAPIView.as_view(), name='checkout'),
    path('status', PaymentStatusAPIView.as_view(), name='payment_status'),
    path("test", razorpay_test_page),

]


