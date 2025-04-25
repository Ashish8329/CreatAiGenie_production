from django.db import models
from base.base_models import BaseModel
from django.contrib.auth import get_user_model
from base.choices import PaymentStatus


class Payment(BaseModel):
    """
    Model representing a payment
    """
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Amount',
        help_text='Amount to be paid'
        )
    payment_id = models.CharField( #razorpay payment id
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name='Payment ID',
        help_text='Unique identifier for the payment'
    )
    order_id = models.CharField( #razorpay order id
        max_length=255,
        unique=True,
        verbose_name='Order ID',
        help_text='Unique identifier for the order'
    )
    signiture = models.CharField( #razorpay signiture
        max_length=255,
        verbose_name='Signiture',
        null=True,
        blank=True,
        help_text='Signiture for the payment'
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices(),
        default=PaymentStatus.CREATED.value[0]
    )

    def __str__(self):
        return f"Payment {self.id} for {self.order_id} - {self.amount}"