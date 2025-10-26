"""
Admin configuration for the payments app.
"""

from django.contrib import admin
from .models import Coupon, CouponUsage, Payment, ActorCost, FinancialReport


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'company', 'actor', 'discount_type', 'discount_value', 'is_active']
    list_filter = ['company', 'discount_type', 'is_active', 'start_date', 'end_date']
    search_fields = ['code', 'company__name']
    readonly_fields = ['created_at']


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'client', 'appointment', 'discount_applied', 'used_at']
    list_filter = ['used_at', 'coupon__company']
    search_fields = ['coupon__code', 'client__username']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'amount', 'method', 'status', 'created_at']
    list_filter = ['method', 'status', 'created_at']
    search_fields = ['appointment__client__username', 'appointment__actor__username']


@admin.register(ActorCost)
class ActorCostAdmin(admin.ModelAdmin):
    list_display = ['actor', 'description', 'amount', 'category', 'date']
    list_filter = ['category', 'date', 'actor__company']
    search_fields = ['actor__username', 'description']


@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    list_display = ['company', 'actor', 'report_type', 'start_date', 'end_date', 'created_at']
    list_filter = ['report_type', 'start_date', 'end_date', 'company']
    search_fields = ['company__name', 'actor__username']