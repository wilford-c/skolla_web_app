import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from students.models import Student

from .models import FeeInvoice
from .models import Payment
from .services import build_signature

User = get_user_model()


class BillingFlowTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin_billing",
            password="pass1234",
            role=User.Role.ADMIN,
        )
        self.guardian = User.objects.create_user(
            username="guardian_billing",
            password="pass1234",
            role=User.Role.GUARDIAN,
        )
        self.student_user = User.objects.create_user(
            username="student_billing",
            password="pass1234",
            role=User.Role.STUDENT,
        )

        self.student = Student.objects.create(
            user=self.student_user,
            admission_number="ST-BILL-001",
            first_name="Ada",
            last_name="Lovelace",
            date_of_birth="2010-01-01",
            guardian_name="Guardian One",
            guardian_user=self.guardian,
        )

        self.invoice = FeeInvoice.objects.create(
            student=self.student,
            description="Tuition Term 1",
            category=FeeInvoice.Category.TUITION,
            amount_due=Decimal("120.00"),
            due_date="2026-04-10",
            created_by=self.admin,
        )

    def test_payment_updates_invoice_status_and_balance(self):
        Payment.objects.create(
            invoice=self.invoice,
            student=self.student,
            amount_paid=Decimal("40.00"),
            method=Payment.Method.ECOCASH,
            status=Payment.Status.SUCCESS,
            recorded_by=self.admin,
        )

        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.amount_paid, Decimal("40.00"))
        self.assertEqual(self.invoice.balance_due, Decimal("80.00"))
        self.assertEqual(self.invoice.status, FeeInvoice.Status.PARTIAL)

    def test_guardian_scope_only_shows_linked_student_invoices(self):
        other_guardian = User.objects.create_user(
            username="guardian_billing_two",
            password="pass1234",
            role=User.Role.GUARDIAN,
        )
        other_student = Student.objects.create(
            admission_number="ST-BILL-002",
            first_name="Grace",
            last_name="Hopper",
            date_of_birth="2010-02-02",
            guardian_name="Guardian Two",
            guardian_user=other_guardian,
        )
        FeeInvoice.objects.create(
            student=other_student,
            description="Exam Fee",
            category=FeeInvoice.Category.EXAM,
            amount_due=Decimal("50.00"),
            due_date="2026-04-15",
            created_by=self.admin,
        )

        self.client.force_login(self.guardian)
        response = self.client.get(reverse("billing:invoice_list"))

        self.assertContains(response, "Tuition Term 1")
        self.assertNotContains(response, "Exam Fee")

    def test_ecocash_payment_is_created_as_pending(self):
        self.client.force_login(self.guardian)
        self.client.post(
            reverse("billing:invoice_pay", args=[self.invoice.pk]),
            {
                "amount_paid": "30.00",
                "method": Payment.Method.ECOCASH,
                "reference": "",
                "notes": "",
            },
        )

        payment = Payment.objects.get(invoice=self.invoice)
        self.invoice.refresh_from_db()

        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertTrue(payment.reference.startswith("ECO-"))
        self.assertEqual(self.invoice.amount_paid, Decimal("0.00"))
        self.assertEqual(self.invoice.status, FeeInvoice.Status.UNPAID)

    def test_ecocash_webhook_success_settles_invoice(self):
        pending_payment = Payment.objects.create(
            invoice=self.invoice,
            student=self.student,
            amount_paid=Decimal("60.00"),
            method=Payment.Method.ECOCASH,
            status=Payment.Status.PENDING,
            recorded_by=self.admin,
            reference="ECO-TEST-001",
        )

        payload = {
            "payment_id": pending_payment.id,
            "status": Payment.Status.SUCCESS,
            "gateway_reference": "ECO-GW-1001",
        }
        raw_body = json.dumps(payload).encode("utf-8")

        response = self.client.post(
            reverse("billing:ecocash_webhook"),
            data=raw_body,
            content_type="application/json",
            HTTP_X_ECOCASH_SIGNATURE=build_signature(raw_body),
        )

        self.assertEqual(response.status_code, 200)

        pending_payment.refresh_from_db()
        self.invoice.refresh_from_db()

        self.assertEqual(pending_payment.status, Payment.Status.SUCCESS)
        self.assertEqual(pending_payment.reference, "ECO-GW-1001")
        self.assertEqual(self.invoice.amount_paid, Decimal("60.00"))
        self.assertEqual(self.invoice.status, FeeInvoice.Status.PARTIAL)

    def test_ecocash_webhook_rejects_invalid_signature(self):
        response = self.client.post(
            reverse("billing:ecocash_webhook"),
            data=json.dumps({"payment_id": 999, "status": Payment.Status.SUCCESS}),
            content_type="application/json",
            HTTP_X_ECOCASH_SIGNATURE="invalid-signature",
        )

        self.assertEqual(response.status_code, 400)
