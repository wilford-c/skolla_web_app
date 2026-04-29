from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from attendance.models import AttendanceRecord, EmailLog, NotificationPreference


class Command(BaseCommand):
    help = "Send daily attendance digest emails for guardians who opted into digest mode."

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            type=str,
            help="Digest date (YYYY-MM-DD). Defaults to previous day.",
        )
        parser.add_argument(
            "--start-date",
            type=str,
            help="Digest start date (YYYY-MM-DD).",
        )
        parser.add_argument(
            "--end-date",
            type=str,
            help="Digest end date (YYYY-MM-DD).",
        )

    def handle(self, *args, **options):
        period_start, period_end = self._resolve_period(
            date_value=options.get("date"),
            start_value=options.get("start_date"),
            end_value=options.get("end_date"),
        )
        sent_emails = 0
        digested_events = 0

        preferences = NotificationPreference.objects.select_related("user").filter(
            is_enabled=True,
            mode=NotificationPreference.NotificationMode.DAILY_DIGEST,
        )

        for preference in preferences:
            recipient_email = preference.get_email()
            if not recipient_email:
                continue

            status_filter = Q()
            if preference.notify_absent:
                status_filter |= Q(status=AttendanceRecord.Status.ABSENT)
            if preference.notify_late:
                status_filter |= Q(status=AttendanceRecord.Status.LATE)
            if preference.notify_excused:
                status_filter |= Q(status=AttendanceRecord.Status.EXCUSED)

            if not status_filter:
                continue

            records = list(
                AttendanceRecord.objects.select_related("student", "classroom", "subject")
                .filter(
                    student__guardian_user=preference.user,
                    date__gte=period_start,
                    date__lte=period_end,
                    digest_sent_at__isnull=True,
                )
                .filter(status_filter)
                .order_by("student__admission_number", "date", "id")
            )

            if not records:
                continue

            grouped_students = self._group_records(records)
            if period_start == period_end:
                period_label = period_start.strftime("%Y-%m-%d")
            else:
                period_label = f"{period_start:%Y-%m-%d} to {period_end:%Y-%m-%d}"

            subject = f"Daily Attendance Digest: {period_label}"
            context = {
                "guardian_name": preference.user.display_name,
                "digest_start": period_start,
                "digest_end": period_end,
                "digest_label": period_label,
                "grouped_students": grouped_students,
                "total_events": len(records),
            }

            email_log = EmailLog.objects.create(
                recipient=preference.user,
                recipient_email=recipient_email,
                subject=subject,
                status=EmailLog.Status.PENDING,
            )

            try:
                send_mail(
                    subject=subject,
                    message=render_to_string("attendance/emails/daily_digest_notification.txt", context),
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@skola.edu"),
                    recipient_list=[recipient_email],
                    html_message=render_to_string("attendance/emails/daily_digest_notification.html", context),
                    fail_silently=False,
                )

                mark_count = AttendanceRecord.objects.filter(
                    id__in=[record.id for record in records],
                    digest_sent_at__isnull=True,
                ).update(digest_sent_at=timezone.now())

                email_log.status = EmailLog.Status.SENT
                email_log.save(update_fields=["status"])

                sent_emails += 1
                digested_events += mark_count
            except Exception as exc:
                email_log.status = EmailLog.Status.FAILED
                email_log.error_message = str(exc)
                email_log.save(update_fields=["status", "error_message"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Sent {sent_emails} digest email(s) for {period_start:%Y-%m-%d} to {period_end:%Y-%m-%d}; marked {digested_events} attendance event(s)."
            )
        )

    def _parse_date(self, value, argument_name):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError as exc:
            raise CommandError(f"{argument_name} must use YYYY-MM-DD format.") from exc

    def _resolve_period(self, *, date_value, start_value, end_value):
        if date_value and (start_value or end_value):
            raise CommandError("Use --date by itself, or use --start-date/--end-date together.")

        if date_value:
            digest_date = self._parse_date(date_value, "--date")
            return digest_date, digest_date

        if bool(start_value) != bool(end_value):
            raise CommandError("--start-date and --end-date must be provided together.")

        if start_value and end_value:
            period_start = self._parse_date(start_value, "--start-date")
            period_end = self._parse_date(end_value, "--end-date")
            if period_end < period_start:
                raise CommandError("--end-date cannot be earlier than --start-date.")
            return period_start, period_end

        default_date = timezone.localdate() - timedelta(days=1)
        return default_date, default_date

    def _group_records(self, records):
        grouped = []
        current_student_id = None
        current_bucket = None

        for record in records:
            if record.student_id != current_student_id:
                current_student_id = record.student_id
                current_bucket = {
                    "student": record.student,
                    "rows": [],
                }
                grouped.append(current_bucket)

            current_bucket["rows"].append(
                {
                    "date": record.date,
                    "status": record.get_status_display(),
                    "classroom": record.classroom.name if record.classroom else "",
                    "subject": record.subject.name if record.subject else "",
                }
            )

        return grouped
