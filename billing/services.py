import hashlib
import hmac
import json
import secrets

from django.conf import settings
from django.utils import timezone

from .models import Payment


ECOCASH_HEADER_SIGNATURE = "HTTP_X_ECOCASH_SIGNATURE"


def _signature_secret() -> str:
    return getattr(settings, "BILLING_ECOCASH_WEBHOOK_SECRET", "dev-ecocash-secret")


def build_signature(raw_body: bytes) -> str:
    secret = _signature_secret().encode("utf-8")
    return hmac.new(secret, raw_body, hashlib.sha256).hexdigest()


def verify_signature(raw_body: bytes, provided_signature: str) -> bool:
    if not provided_signature:
        return False
    expected_signature = build_signature(raw_body)
    return hmac.compare_digest(expected_signature, provided_signature)


def create_gateway_reference() -> str:
    return f"ECO-{timezone.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(4).upper()}"


def append_payment_note(payment: Payment, note: str):
    note = note.strip()
    if not note:
        return

    if payment.notes:
        payment.notes = f"{payment.notes}\n{note}"
    else:
        payment.notes = note


def initiate_ecocash_payment(payment: Payment):
    if not payment.reference:
        payment.reference = create_gateway_reference()

    append_payment_note(
        payment,
        f"[{timezone.now().isoformat()}] EcoCash payment initiated and awaiting callback confirmation.",
    )
    payment.save(update_fields=["reference", "notes"])


def apply_ecocash_gateway_status(payment: Payment, gateway_status: str, payload: dict | None = None):
    status_value = (gateway_status or "").strip().upper()
    if status_value not in {Payment.Status.PENDING, Payment.Status.SUCCESS, Payment.Status.FAILED}:
        raise ValueError("Unsupported gateway status")

    gateway_reference = (payload or {}).get("gateway_reference") or (payload or {}).get("reference")
    if gateway_reference:
        payment.reference = str(gateway_reference)[:120]

    old_status = payment.status
    payment.status = status_value

    note_suffix = ""
    if payload:
        payload_excerpt = json.dumps(payload, sort_keys=True)[:500]
        note_suffix = f" payload={payload_excerpt}"

    append_payment_note(
        payment,
        f"[{timezone.now().isoformat()}] Gateway callback: {old_status} -> {payment.status}.{note_suffix}",
    )
    payment.save(update_fields=["status", "reference", "notes"])
