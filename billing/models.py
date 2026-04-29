from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from students.models import Student


class FeeInvoice(models.Model):
    """Fee invoices for students."""

    class Status(models.TextChoices):
        UNPAID = "UNPAID", "Unpaid"
        PARTIAL = "PARTIAL", "Partially Paid"
        PAID = "PAID", "Paid"
        VOID = "VOID", "Void"

    class Category(models.TextChoices):
        TUITION = "TUITION", "Tuition"
        EXAM = "EXAM", "Exam"
        TRANSPORT = "TRANSPORT", "Transport"
        ACTIVITY = "ACTIVITY", "Activity"
        OTHER = "OTHER", "Other"

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="invoices",
    )
    description = models.CharField(max_length=255)
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.TUITION,
    )
    amount_due = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    due_date = models.DateField()
    issued_on = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UNPAID)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_invoices",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-due_date", "-created_at"]
        indexes = [
            models.Index(fields=["student", "status"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self) -> str:
        return f"INV-{self.id} {self.student.admission_number} {self.description}"

    @property
    def balance_due(self) -> Decimal:
        return max(self.amount_due - self.amount_paid, Decimal("0.00"))

    @property
    def is_overdue(self) -> bool:
        return (
            self.status in {self.Status.UNPAID, self.Status.PARTIAL}
            and self.due_date < timezone.localdate()
        )

    @property
    def has_pending_payment(self) -> bool:
        return self.payments.filter(status=Payment.Status.PENDING).exists()

    def clean(self):
        super().clean()
        if self.amount_paid > self.amount_due:
            raise ValidationError("Amount paid cannot exceed amount due.")

    def refresh_payment_state(self, save: bool = True):
        paid_total = (
            self.payments.filter(status=Payment.Status.SUCCESS).aggregate(
                total=Coalesce(Sum("amount_paid"), Decimal("0.00"))
            )["total"]
            or Decimal("0.00")
        )
        self.amount_paid = paid_total

        if self.status != self.Status.VOID:
            if paid_total <= 0:
                self.status = self.Status.UNPAID
            elif paid_total < self.amount_due:
                self.status = self.Status.PARTIAL
            else:
                self.status = self.Status.PAID

        if save:
            self.save(update_fields=["amount_paid", "status", "updated_at"])


class Payment(models.Model):
    """Payments recorded against invoices."""

    class Method(models.TextChoices):
        ECOCASH = "ECOCASH", "EcoCash"
        CARD = "CARD", "Credit/Debit Card"
        BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
        CASH = "CASH", "Cash"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    invoice = models.ForeignKey(
        FeeInvoice,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.ECOCASH)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUCCESS)
    reference = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    paid_at = models.DateTimeField(default=timezone.now)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="recorded_payments",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-paid_at", "-created_at"]
        indexes = [
            models.Index(fields=["invoice", "status"]),
            models.Index(fields=["student", "-paid_at"]),
        ]

    def __str__(self) -> str:
        return f"Payment {self.id} for INV-{self.invoice_id}"

    def clean(self):
        super().clean()

        if self.invoice_id and self.student_id and self.invoice.student_id != self.student_id:
            raise ValidationError("Payment student must match the invoice student.")

        if self.invoice_id and self.status == self.Status.SUCCESS:
            previous_success_amount = Decimal("0.00")
            if self.pk:
                previous = Payment.objects.filter(pk=self.pk).first()
                if previous and previous.status == self.Status.SUCCESS:
                    previous_success_amount = previous.amount_paid

            outstanding_before = self.invoice.balance_due + previous_success_amount
            if self.amount_paid > outstanding_before:
                raise ValidationError("Payment amount exceeds the invoice balance due.")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            self.invoice.refresh_payment_state(save=True)

    def delete(self, *args, **kwargs):
        invoice = self.invoice
        with transaction.atomic():
            super().delete(*args, **kwargs)
            invoice.refresh_payment_state(save=True)
