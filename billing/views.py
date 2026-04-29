import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from auditlog.services import log_event

from .forms import FeeInvoiceForm
from .forms import QuickPaymentForm
from .models import FeeInvoice
from .models import Payment
from .services import apply_ecocash_gateway_status
from .services import initiate_ecocash_payment
from .services import verify_signature

User = get_user_model()


def _is_admin_or_staff(user):
    return user.is_superuser or user.role in {User.Role.ADMIN, User.Role.STAFF}


def _invoice_queryset_for_user(user):
    queryset = FeeInvoice.objects.select_related(
        "student",
        "student__user",
        "student__guardian_user",
    )

    if _is_admin_or_staff(user):
        return queryset

    if user.role == User.Role.GUARDIAN:
        return queryset.filter(student__guardian_user=user)

    if user.role == User.Role.STUDENT:
        return queryset.filter(student__user=user)

    return queryset.none()


def _user_can_pay_invoice(user, invoice):
    if _is_admin_or_staff(user):
        return True

    if user.role == User.Role.GUARDIAN:
        return invoice.student.guardian_user_id == user.id

    if user.role == User.Role.STUDENT:
        return invoice.student.user_id == user.id

    return False


def _has_pending_ecocash(invoice):
    return invoice.payments.filter(
        method=Payment.Method.ECOCASH,
        status=Payment.Status.PENDING,
    ).exists()


@login_required
def invoice_list(request):
    invoices = _invoice_queryset_for_user(request.user)

    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()
    student_filter = request.GET.get("student", "").strip()

    if query:
        invoices = invoices.filter(
            Q(description__icontains=query)
            | Q(student__admission_number__icontains=query)
            | Q(student__first_name__icontains=query)
            | Q(student__last_name__icontains=query)
        )

    if status_filter == "OVERDUE":
        invoices = invoices.filter(
            status__in=[FeeInvoice.Status.UNPAID, FeeInvoice.Status.PARTIAL],
            due_date__lt=timezone.localdate(),
        )
    elif status_filter in dict(FeeInvoice.Status.choices):
        invoices = invoices.filter(status=status_filter)

    if student_filter and _is_admin_or_staff(request.user):
        invoices = invoices.filter(student_id=student_filter)

    totals = invoices.aggregate(
        total_billed=Coalesce(Sum("amount_due"), Decimal("0.00")),
        total_collected=Coalesce(Sum("amount_paid"), Decimal("0.00")),
    )

    total_billed = totals["total_billed"] or Decimal("0.00")
    total_collected = totals["total_collected"] or Decimal("0.00")

    context = {
        "invoices": invoices,
        "students": _invoice_queryset_for_user(request.user)
        .values("student_id", "student__admission_number", "student__first_name", "student__last_name")
        .distinct()
        .order_by("student__admission_number"),
        "can_manage_billing": _is_admin_or_staff(request.user),
        "can_make_payment": request.user.role
        in {User.Role.ADMIN, User.Role.STAFF, User.Role.GUARDIAN, User.Role.STUDENT}
        or request.user.is_superuser,
        "status_options": [("", "All statuses"), ("OVERDUE", "Overdue"), *FeeInvoice.Status.choices],
        "selected_status": status_filter,
        "selected_student": student_filter,
        "query": query,
        "total_billed": total_billed,
        "total_collected": total_collected,
        "total_outstanding": total_billed - total_collected,
    }
    return render(request, "billing/invoice_list.html", context)


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF)
def invoice_create(request):
    form = FeeInvoiceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        invoice = form.save(commit=False)
        invoice.created_by = request.user
        invoice.save()
        log_event(
            request=request,
            action="billing.invoice.create",
            entity_type="FeeInvoice",
            entity_id=str(invoice.pk),
            description=f"Created invoice INV-{invoice.pk} for student {invoice.student.admission_number}.",
        )
        messages.success(request, "Invoice created successfully.")
        return redirect("billing:invoice_list")

    return render(
        request,
        "billing/invoice_form.html",
        {
            "form": form,
            "window_title": "New Invoice - Skola",
            "page_title": "Create Invoice",
            "submit_label": "Save Invoice",
        },
    )


@login_required
@role_required(User.Role.ADMIN, User.Role.STAFF)
def invoice_update(request, pk):
    invoice = get_object_or_404(FeeInvoice, pk=pk)
    form = FeeInvoiceForm(request.POST or None, instance=invoice)
    if request.method == "POST" and form.is_valid():
        updated = form.save()
        log_event(
            request=request,
            action="billing.invoice.update",
            entity_type="FeeInvoice",
            entity_id=str(updated.pk),
            description=f"Updated invoice INV-{updated.pk}.",
            metadata={"status": updated.status},
        )
        messages.success(request, "Invoice updated successfully.")
        return redirect("billing:invoice_detail", pk=invoice.pk)

    return render(
        request,
        "billing/invoice_form.html",
        {
            "form": form,
            "window_title": "Edit Invoice - Skola",
            "page_title": f"Edit Invoice INV-{invoice.id}",
            "submit_label": "Update Invoice",
        },
    )


@login_required
@role_required(User.Role.ADMIN)
@require_POST
def invoice_delete(request, pk):
    invoice = get_object_or_404(FeeInvoice, pk=pk)
    invoice_id = str(invoice.pk)
    invoice.delete()
    log_event(
        request=request,
        action="billing.invoice.delete",
        entity_type="FeeInvoice",
        entity_id=invoice_id,
        description=f"Deleted invoice INV-{invoice_id}.",
        severity="WARNING",
    )
    messages.success(request, "Invoice deleted successfully.")
    return redirect("billing:invoice_list")


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(_invoice_queryset_for_user(request.user), pk=pk)
    payments = invoice.payments.select_related("recorded_by").all()

    can_pay = _user_can_pay_invoice(request.user, invoice) and invoice.status not in {
        FeeInvoice.Status.PAID,
        FeeInvoice.Status.VOID,
    }

    context = {
        "invoice": invoice,
        "payments": payments,
        "can_manage_billing": _is_admin_or_staff(request.user),
        "can_pay": can_pay,
        "quick_payment_form": QuickPaymentForm(invoice=invoice),
    }
    return render(request, "billing/invoice_detail.html", context)


@login_required
@require_POST
def invoice_pay(request, pk):
    invoice = get_object_or_404(_invoice_queryset_for_user(request.user), pk=pk)

    if not _user_can_pay_invoice(request.user, invoice):
        raise PermissionDenied

    if invoice.status in {FeeInvoice.Status.PAID, FeeInvoice.Status.VOID}:
        messages.error(request, "This invoice is not payable.")
        return redirect("billing:invoice_detail", pk=invoice.pk)

    form = QuickPaymentForm(request.POST or None, invoice=invoice)
    if not form.is_valid():
        messages.error(request, "Please provide a valid payment amount and method.")
        return redirect("billing:invoice_detail", pk=invoice.pk)

    method = form.cleaned_data["method"]
    if method == Payment.Method.ECOCASH and _has_pending_ecocash(invoice):
        messages.warning(
            request,
            "An EcoCash payment is already pending for this invoice. Wait for callback confirmation.",
        )
        return redirect("billing:invoice_detail", pk=invoice.pk)

    payment = form.save(commit=False)
    payment.invoice = invoice
    payment.student = invoice.student
    payment.recorded_by = request.user
    payment.status = Payment.Status.SUCCESS
    if method == Payment.Method.ECOCASH:
        payment.status = Payment.Status.PENDING

    payment.full_clean()
    payment.save()

    log_event(
        request=request,
        action="billing.payment.record",
        entity_type="Payment",
        entity_id=str(payment.pk),
        description=f"Recorded {payment.method} payment for invoice INV-{invoice.pk}.",
        metadata={
            "invoice_id": invoice.pk,
            "amount_paid": str(payment.amount_paid),
            "status": payment.status,
        },
    )

    if method == Payment.Method.ECOCASH:
        initiate_ecocash_payment(payment)
        messages.info(request, "EcoCash payment created and is awaiting gateway confirmation.")
    else:
        messages.success(request, "Payment recorded successfully.")

    invoice.refresh_from_db()

    if request.headers.get("HX-Request"):
        return render(
            request,
            "billing/partials/invoice_row.html",
            {
                "invoice": invoice,
                "can_manage_billing": _is_admin_or_staff(request.user),
                "can_make_payment": _user_can_pay_invoice(request.user, invoice),
            },
        )

    next_url = request.POST.get("next")
    if next_url:
        return redirect(next_url)

    return redirect("billing:invoice_detail", pk=invoice.pk)


@csrf_exempt
@require_POST
def ecocash_webhook(request):
    signature = request.META.get("HTTP_X_ECOCASH_SIGNATURE", "")
    if not verify_signature(request.body, signature):
        return HttpResponseBadRequest("Invalid signature")

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    payment_id = payload.get("payment_id")
    reference = payload.get("reference")
    gateway_status = payload.get("status", "")

    payment = None
    if payment_id:
        payment = Payment.objects.filter(
            id=payment_id,
            method=Payment.Method.ECOCASH,
        ).select_related("invoice").first()

    if payment is None and reference:
        payment = Payment.objects.filter(
            reference=reference,
            method=Payment.Method.ECOCASH,
        ).select_related("invoice").first()

    if payment is None:
        return HttpResponseBadRequest("Payment not found")

    try:
        apply_ecocash_gateway_status(payment, gateway_status, payload=payload)
    except ValueError as exc:
        return HttpResponseBadRequest(str(exc))

    return JsonResponse(
        {
            "ok": True,
            "payment_id": payment.id,
            "invoice_id": payment.invoice_id,
            "status": payment.status,
        }
    )
