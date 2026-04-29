from django import forms

from students.models import Student

from .models import FeeInvoice
from .models import Payment


class FeeInvoiceForm(forms.ModelForm):
    due_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    issued_on = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), required=False)

    class Meta:
        model = FeeInvoice
        fields = [
            "student",
            "description",
            "category",
            "amount_due",
            "due_date",
            "issued_on",
            "status",
            "notes",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["student"].queryset = Student.objects.filter(
            status=Student.Status.ACTIVE
        ).order_by("admission_number")


class QuickPaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["amount_paid", "method", "reference", "notes"]

    def __init__(self, *args, invoice=None, **kwargs):
        self.invoice = invoice
        super().__init__(*args, **kwargs)
        if invoice and not self.is_bound:
            self.fields["amount_paid"].initial = invoice.balance_due

    def clean_amount_paid(self):
        amount = self.cleaned_data["amount_paid"]
        if self.invoice and amount > self.invoice.balance_due:
            raise forms.ValidationError("Amount cannot exceed the remaining balance.")
        return amount
