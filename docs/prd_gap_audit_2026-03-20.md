# PRD Gap Audit (2026-03-20)

## Scope
Audit compares the current codebase against new_prd.md requirements for MVP and post-MVP capabilities.

## Evidence Snapshot
- Main app routing is server-rendered Django app modules with no API namespace in [config/urls.py](../config/urls.py).
- Billing supports invoice/payment domain and EcoCash webhook callback in [billing/urls.py](../billing/urls.py) and [billing/views.py](../billing/views.py).
- Attendance includes per-class/per-subject records and report exports/templates in [attendance/models.py](../attendance/models.py) and [attendance/urls.py](../attendance/urls.py).
- No PWA/service worker assets found in static files.
- No DRF usage found in Python source.

## PRD Coverage Matrix

### Core MVP
- User and role management: PARTIAL
  - Implemented: custom role-based user model and auth views in [accounts/models.py](../accounts/models.py) and [accounts/urls.py](../accounts/urls.py).
  - Missing from PRD target: django-allauth/SSO/MFA and group/permission policy model.
- Student information system: PARTIAL
  - Implemented: student profiles, import/export, guardian linkage in [students/models.py](../students/models.py) and [students/urls.py](../students/urls.py).
  - Missing from PRD target: dedicated Enrollment entity and full class registration lifecycle.
- Academic management: PARTIAL
  - Implemented: classrooms, subjects, assessments, gradebook and bulk entry in [academics/urls.py](../academics/urls.py).
  - Missing from PRD target: conflict-aware timetable scheduler and report-card generation workflow.
- Attendance tracking: PARTIAL
  - Implemented: per-class/per-subject attendance, reports, export CSV/PDF, notification preferences in [attendance/urls.py](../attendance/urls.py).
  - Missing from PRD target: QR attendance and geofencing/geolocation capture.
- Financial management: PARTIAL
  - Implemented: invoicing, payments, pending gateway flow, callback signature verification in [billing/models.py](../billing/models.py), [billing/views.py](../billing/views.py), [billing/services.py](../billing/services.py).
  - Missing from PRD target: outbound EcoCash sandbox API integration and reconciliation/retry workflow.
- Parent and student portals: COMPLETE (MVP level)
  - Implemented dashboards and role-specific views in [accounts/views.py](../accounts/views.py) and [skola/templates/dashboard.html](../skola/templates/dashboard.html).
- Communication: PARTIAL
  - Implemented in-app messaging, announcements, notification center in [messaging/urls.py](../messaging/urls.py), [announcements/urls.py](../announcements/urls.py), [notifications/urls.py](../notifications/urls.py).
  - Missing from PRD target: SMS broadcast integration and scheduled campaign dispatch via background workers.
- Basic reporting and analytics: COMPLETE (MVP level)
  - Implemented attendance analytics and exports in [attendance/views.py](../attendance/views.py).

### Data and API
- Data model breadth: PARTIAL
  - Implemented key entities (student, class, subject, attendance, fees, payments, messaging).
  - Missing: explicit Enrollment model and broader normalized PRD entities (some modeled implicitly).
- REST API surface: MISSING
  - No DRF or API endpoint layer present; PRD expects /api/* endpoints.

### Platform and Architecture
- Offline/PWA strategy: MISSING
  - No service worker, manifest, background sync or IndexedDB client assets present.
- Asynchronous background tasks: MISSING
  - No Celery task layer detected for SMS/email batching, export jobs, or webhook retries.
- Mobile push notifications (FCM): MISSING
- Multi-branch/campus partitioning: MISSING
- Deployment automation (Docker/CI from PRD plan): PARTIAL
  - Some docs exist, but no Dockerfile/CI workflows found in repo.

### Security and Compliance
- Baseline security: PARTIAL
  - Django auth and role checks exist in [accounts/decorators.py](../accounts/decorators.py).
  - Missing from PRD target: MFA, richer audit logging, policy-level compliance controls.

## Priority Backlog (Recommended)
1. Build DRF API layer for MVP resources (auth, students, classes, attendance, fees, payments, notifications).
2. Implement real EcoCash sandbox initiation + idempotent webhook reconciliation queue.
3. Add SMS provider integration (alerts and broadcasts) with delivery logs.
4. Add PWA baseline (manifest + service worker + offline fallback + queued attendance sync).
5. Add Enrollment model and registration workflow (student-class history).
6. Add async task runtime (Celery + Redis) for notifications, exports, retries.
7. Add timetable conflict-checking module.
8. Add audit log model and sensitive action tracking.

## Suggested Next Sprint Slice
- Sprint target: API + payment reliability
- Deliverables:
  - DRF endpoints for /api/students, /api/classes, /api/attendance/mark, /api/fees, /api/payments
  - EcoCash initiation adapter and webhook idempotency table
  - Basic reconciliation admin view for pending/failed transactions
