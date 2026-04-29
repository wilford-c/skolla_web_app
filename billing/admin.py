from django.contrib import admin

from .models import FeeInvoice
from .models import Payment


@admin.register(FeeInvoice)
class FeeInvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "description",
        "category",
        "amount_due",
        "amount_paid",
        "status",
        "due_date",
    )
    list_filter = ("status", "category", "due_date")
    search_fields = (
        "description",
        "student__admission_number",
        "student__first_name",
        "student__last_name",
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "invoice",
        "student",
        "amount_paid",
        "method",
        "status",
        "paid_at",
    )
    list_filter = ("method", "status", "paid_at")
    search_fields = (
        "reference",
        "student__admission_number",
        "student__first_name",
        "student__last_name",
    )
