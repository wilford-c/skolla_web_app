# Skola PRD Brief for Squad

Source of truth:
- docs/prd.md (Version 2.0, 2026-02-04)

## Product Direction
- Build a unified school management platform on Django.
- Prioritize role-aware workflows for admin, staff, teacher, student, and guardian.
- Keep server-rendered UX fast, simple, and maintainable.

## In-Scope Capabilities (v2.0)
- Authentication and role-based access control.
- Student lifecycle management.
- Classroom and subject management.
- Attendance capture, reporting, and analytics.
- Guardian portal and family visibility.
- Audit logging and exports (CSV/PDF).

## Quality Targets
- P95 page load under 2 seconds.
- Reliability target 99.5% uptime.
- Test coverage target above 80%.
- WCAG AA accessibility posture.

## Current Sprint Context (Apr 2026)
- Financial management reliability and integration hardening.
- Expand automated test coverage for critical workflows.
- Improve notification pipeline readiness (scheduler/async work).
- Close non-functional evidence gaps (performance and accessibility validation).

## Squad Working Rules
- Use docs/prd.md for requirements and acceptance criteria before implementation.
- Check docs/prd_implementation_audit_2026-03-25.md for implemented vs pending items.
- Prefer incremental, test-backed changes in small pull requests.
- Keep role/permission checks explicit for every new endpoint or view.
