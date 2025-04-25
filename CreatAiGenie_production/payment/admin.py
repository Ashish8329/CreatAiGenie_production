from django.contrib import admin
from base.base_admin import BaseAdmin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'status', 'created_at')
    search_fields = ('amount', 'status')
    list_filter = ('status',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
