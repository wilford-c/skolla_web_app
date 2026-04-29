# Skola Platform Product Requirements Document (PRD)

**Version:** 2.0  
**Date:** 4 February 2026  
**Status:** Active Development  
**Classification:** Internal – Product Team  
**Author:** Product Management Team  
**Sprint Coverage:** Sprint 5 & Beyond (2 Feb – 13 Feb 2026)

---

## Table of Contents
(To be generated in Microsoft Word via *Insert → Table of Contents*)

---

## 1. Executive Summary
Skola is a comprehensive school management platform designed to transform educational administration through a unified digital solution. Built on Django with a clean, intuitive interface, Skola covers the full student lifecycle—admissions, academics, attendance, reporting, and institutional oversight. This document captures the full product vision, requirements, user stories, and roadmap, serving as the single source of truth for stakeholders and delivery teams.

### 1.1 Vision Statement
Empower educational institutions with a unified, scalable, and user-friendly platform that streamlines administrative workflows, enhances data-driven decision making, and elevates educational outcomes.

### 1.2 Key Value Propositions
- Unified data management across students, staff, and academics.
- Role-based access control ensuring secure, context-aware permissions.
- Operational efficiency: automated workflows reduce manual effort up to 60%.
- Real-time insights delivered through dashboards and analytics.
- Scalable architecture supporting 100 to 10,000+ students.
- Compliance-ready foundation with audit trails and data retention.

---

## 2. Product Overview
### 2.1 Product Description
Skola is a lightweight yet powerful Django platform with minimal front-end overhead, optimized for speed and maintainability. It streamlines authentication, student information management, classroom/subject curation, attendance workflows, and institutional reporting.

### 2.2 Core Capabilities
| Module | Description | Target Users |
| --- | --- | --- |
| Authentication & Authorization | Multi-role user management with secure permissions | All Users |
| Student Information System | Full student lifecycle tracking | Admin, Staff |
| Academic Management | Classroom, subject, and curriculum orchestration | Admin, Teachers |
| Attendance System | Real-time capture with analytics | Teachers, Admin |
| Reporting & Analytics | Dashboards and exports for decision-making | Admin, Management |
| Communication Hub | (Future) Notifications and parent-teacher messaging | All Users |
| Financial Management | (Future) Fee collection and payment tracking | Admin, Finance |

### 2.3 Technology Stack
| Layer | Technology | Version | Purpose |
| --- | --- | --- | --- |
| Backend Framework | Django | 4.2+ | Core application stack |
| Database | PostgreSQL / SQLite | 13+ / 3.x | Persistence | 
| Template Engine | Django Templates | Built-in | Server-side rendering |
| Frontend | HTML / CSS / JS | Native | Lightweight UI |
| Environment Config | django-environ | Latest | Env var management |
| Deployment | WSGI / ASGI | Standard | Production servers |

---

## 3. Objectives & Success Metrics
| Objective | Key Results | Metric | Target | Status |
| --- | --- | --- | --- | --- |
| Modular Architecture | Settings split by environment | Config complexity score | < 5 files | ✅ Complete |
| Zero-Downtime Deployment | `.env` driven configuration | Deployment success rate | 100% | ✅ Complete |
| Data Integrity | Referential integrity maintained | Consistency checks | Pass | ✅ Complete |
| User Adoption | Intuitive workflows | Time-to-productivity | < 2 hours | 🔄 In Progress |
| Performance | Fast response times | P95 load time | < 2 s | 🔄 In Progress |
| Test Coverage | Automated safety net | Code coverage | > 80% | ❌ Planned |

---

## 4. User Personas
### 4.1 Sarah Thompson – School Administrator
- **Role:** Admin | **Age:** 38 | **Experience:** 12 years | **Tech:** High | **Usage:** Daily (6–8h)
- **Goals:** Maintain student data, oversee academics, manage users, produce reports, monitor KPIs.
- **Pain Points:** Disconnected systems, complex reporting, slow provisioning, limited real-time visibility.

### 4.2 James Martinez – Mathematics Teacher
- **Role:** Teacher | **Age:** 31 | **Experience:** 7 years | **Tech:** Medium | **Usage:** Daily (1–2h)
- **Goals:** Rapid attendance, access rosters, view performance, communicate with parents, minimize admin.
- **Pain Points:** Slow tools, lack of mobile access, weak historical context, poor gradebook integration.

### 4.3 Linda Chen – Administrative Staff
- **Role:** Staff | **Age:** 45 | **Experience:** 15 years | **Tech:** Medium | **Usage:** Daily (4–6h)
- **Goals:** Efficient enrollments, accurate records, support teachers/parents, maintain data quality.
- **Pain Points:** Repetitive entry, unclear permissions, difficulty finding history, manual verification.

### 4.4 Maria Rodriguez – Parent/Guardian
- **Role:** Guardian | **Age:** 42 | **Tech:** Medium | **Usage:** Weekly (30m)
- **Goals:** Monitor attendance in real time, receive notifications, manage multiple kids from one login, stay informed without calling the office.
- **Pain Points:** Fragmented updates, lack of read-only portal access, missed communications, duplicate logins for each child.

### 4.5 David Okonkwo – Student
- **Role:** Student | **Age:** 16 | **Tech:** High | **Usage:** Daily (2–3h)
- **Goals:** View schedules, attendance, grades, submit assignments, communicate with teachers.
- **Pain Points:** Limited self-service, fragmented tools, unclear deadlines, reliance on parents for info.

---

## 5. Scope Definition
### 5.1 In Scope – Release v2.0
- Cookiecutter-Django architecture
- Env-based configuration management
- Comprehensive auth/roles
- Student information management
- Classroom & subject management
- Daily attendance tracking & reporting
- Role-based dashboards & analytics
- Role-aware navigation and personalized dashboards per role (admin, staff, teacher, student, guardian)
- Guardian/Parent portal with linked student attendance overviews
- Audit logging for critical operations
- Data exports (CSV, PDF)
- Responsive design for desktop/tablet

### 5.2 Out of Scope – Future Roadmap
- Payment processing & fee management (Stripe – Q2 2026)
- Parent portal & mobile applications (Q3 2026)
- LMS features (Q4 2026)
- Advanced analytics/predictive insights (2027)
- Multi-language support (2027)
- Third-party integrations & API ecosystem (2027)

### 5.3 Assumptions
- Users have basic computer literacy and internet access.
- Schools provide adequate infrastructure.
- Single-institution deployment (no multi-tenancy).
- English is the primary language.
- Academic calendar follows standard semester system.
- Institutions maintain student data privacy policies.

### 5.4 Dependencies
- Django framework stability.
- PostgreSQL availability for production environments.
- School IT infrastructure reliability.
- Stakeholder availability for UAT.
- Completion of training resources and documentation.

---

## 6. User Stories & Acceptance Criteria
Stories grouped by epic and prioritized using MoSCoW.

### EPIC 1: Authentication & Authorization
- **US-101:** User Registration with Role Assignment *(Must – 8 pts)*
- **US-102:** Secure User Login *(Must – 5 pts)*
- **US-103:** Role-Based Dashboard Routing *(Must – 5 pts)*
- **US-104:** Password Reset Workflow *(Should – 5 pts)*
- **US-105:** User Profile Management *(Should – 3 pts)*
- **US-106:** Session Management & Logout *(Must – 2 pts)*
- **US-107:** Role-Based Navigation & Access States *(Must – 5 pts)*

### EPIC 2: Student Information System
- **US-201:** Student Enrollment & Registration *(Must – 8 pts)*
- **US-202:** Student Information Viewing & Search *(Must – 5 pts)*
- **US-203:** Student Information Update *(Must – 5 pts)*
- **US-204:** Student Status Management *(Must – 3 pts)*
- **US-205:** Bulk Student Import *(Should – 8 pts)*
- **US-206:** Student Data Export *(Should – 5 pts)*

### EPIC 3: Academic Management
- **US-301:** Classroom Creation & Management *(Must – 5 pts)*
- **US-302:** Subject Creation & Scheduling *(Must – 5 pts)*
- **US-303:** Student-Classroom Assignment *(Must – 5 pts)*
- **US-304:** Teacher-Subject Assignment *(Must – 3 pts)*
- **US-305:** Academic Calendar Management *(Should – 8 pts)*
- **US-306:** Timetable/Schedule Management *(Could – 13 pts)*

### EPIC 4: Attendance Management
- **US-401:** Daily Attendance Recording *(Must – 8 pts)*
- **US-402:** Attendance History & Reports *(Must – 8 pts)*
- **US-403:** Attendance Dashboard Widgets *(Must – 5 pts)*
- **US-404:** Attendance Correction & Audit *(Must – 5 pts)*
- **US-405:** Automated Attendance Alerts *(Should – 8 pts)*
- **US-406:** Attendance Integration with Student Records *(Should – 3 pts)*
- **US-407:** Custom Attendance Report Builder *(Should – 8 pts)*
- **US-408:** Attendance Analytics Dashboard with Trends *(Should – 8 pts)*
- **US-409:** PDF Report Generation with Charts *(Should – 5 pts)*

### EPIC 5: Family Engagement & Guardian Portal
- **US-501:** Guardian Account Creation & Student Linking *(Must – 8 pts)*
- **US-502:** Guardian Attendance Dashboard *(Must – 8 pts)*
- **US-503:** Family Notifications & Messaging Hooks *(Should – 5 pts)*
- **US-504:** Email Alert Configuration System *(Should – 8 pts)*
- **US-505:** SMS Integration Setup *(Should – 13 pts)*
- **US-506:** Guardian Notification Preferences *(Should – 5 pts)*

Each story includes detailed acceptance criteria, dependencies, and notes as provided in the user specification.

---

## 7. Functional Requirements
### 7.1 Authentication & Authorization
Custom user model, password policy, session timeout, account lockout, RBAC with 403 handling, audit logging, HTTPS enforcement, CSRF protection, and role-aware navigation that exposes only the modules applicable to each persona (admin, staff, teacher, student, guardian).

### 7.2 Student Information System
Unique admission numbers, guardian validation, status management, search/filter functionality, pagination, data exports, audit trail for CRUD operations, and the ability to link multiple student records to a guardian/parent portal account for read-only visibility.

### 7.3 Academic Management
Classroom/subject uniqueness, teacher assignment, capacity tracking, archival options, relationship enforcement, bulk tools, calendar support.

### 7.4 Attendance Management
Per-student per-subject records, status enumeration, unique constraints, draft autosave, correction workflow, dashboards tailored per role (admin overview, teacher workload, student self-view, guardian read-only summaries), analytics, alerting, exports.

---

## 8. Non-Functional Requirements
### 8.1 Performance
P95 page load < 2s, optimized queries, pagination, caching, support for 100+ concurrent users, CDN for static assets.

### 8.2 Security
Mandatory HTTPS in production, secure cookies, CSRF/XSS/SQLi protection, env-managed secrets, encrypted backups, rate limiting, security headers, dependency updates.

### 8.3 Reliability
99.5% uptime target, automated backups, health checks, error logging, migration testing, rollback plans.

### 8.4 Usability
Responsive design for desktop/tablet, keyboard navigation, WCAG AA contrast, consistent UX, inline validation, loading indicators, contextual help.

### 8.5 Maintainability
Cookiecutter layout, modular apps, code comments for complex logic, typed helpers, environment-split requirements, linting, documented workflows.

### 8.6 Scalability
PostgreSQL for production, stateless app design, database indexing, async tasks (future), object storage for files, microservice consideration later.

### 8.7 Compliance & Data Privacy
FERPA alignment, GDPR considerations, audit logs, role-based visibility, data export/portability, future anonymization/consent management.

---

## 9. Data Model & Schema
- **User (`accounts.User`)** – UUID PK, unique username/email, role field, relations to classrooms/subjects/attendance.
- **Student (`students.Student`)** – UUID PK, unique admission number, optional linked user, demographic fields, guardian contacts, optional `guardian_user` (portal link), status, timestamps.
- **Classroom (`academics.Classroom`)** – UUID PK, unique code/name, optional homeroom teacher, capacity, active flag, timestamps.
- **Subject (`academics.Subject`)** – UUID PK, code unique per classroom, weekly sessions, teacher assignment, active flag.
- **ClassroomEnrollment** – (Future) many-to-many mapping with status history.
- **AttendanceRecord (`attendance.AttendanceRecord`)** – UUID PK, student/classroom/subject FKs, date, status, notes, recorded_by, timestamps, uniqueness constraint.

---

## 10. System Architecture
### 10.1 High-Level View
```
Browser (HTTPS)
    ↓
Reverse Proxy (Nginx)
    ↓
Django App (URLs → Views → Templates)
    ↓
Django ORM
    ↓
PostgreSQL / SQLite

Supporting services: CDN (static files), Object Storage (media), SMTP (email), Centralized Logging
```

### 10.2 Application Structure
| Directory | Purpose |
| --- | --- |
| config/ | Project configuration |
| config/settings/ | base, local, production |
| config/urls.py | Root routing |
| accounts/, students/, academics/, attendance/ | Domain logic |
| templates/, static/ | Presentation assets |
| requirements/ | Dependency sets |
| manage.py | Django entry point |

### 10.3 Deployment Architecture
- Server: Ubuntu 20.04 LTS (cloud/on-prem)
- Python 3.10+ virtual environment
- Gunicorn/uWSGI behind Nginx
- PostgreSQL 13+ (separate host recommended)
- SSL via Let’s Encrypt, firewall rules, monitoring/logging/backups

---

## 11. Key User Flows
1. **Student Enrollment Flow:** Login → Students → Add → Validate → Submit → Optional portal account.
2. **Daily Attendance Recording:** Dashboard → Select subject → Mark statuses → Autosave → Submit.
3. **Attendance Report Generation:** Attendance → Reports → Filter → Generate → Export.
4. **Classroom & Subject Setup:** Academics → Create classroom → Assign teacher → Create subjects → Assign teachers.
5. **Guardian Family Overview:** Guardian login → Dashboard auto-filters linked students → Review per-child attendance summaries → Drill into recent records if needed.

---

## 12. Release Plan & Roadmap
### 12.1 Sprint 5 Deliverables (2–13 Feb 2026)
- Cookiecutter architecture ✅
- Environment configuration ✅
- Requirements matrix ✅
- Documentation refresh & PRD ✅
- Manual regression ✅

### 12.2 Future Sprints
| Sprint | Timeline | Focus | Key Deliverables |
| --- | --- | --- | --- |
| 6 | 16–27 Feb | Automated Testing | Pytest, CI/CD foundations, >60% coverage |
| 7 | 2–13 Mar | Enhanced Reporting | Advanced analytics, exports, builder |
| 8 | 16–27 Mar | Communication Module | Email/SMS alerts, in-app messaging |
| 9 | 30 Mar – 10 Apr | Parent Portal (Phase 1) | Parent dashboards, messaging |
| 10 | 13–24 Apr | Financial Management | Fee structure, Stripe integration |
| 11–12 | 27 Apr – 22 May | LMS Features | Assignments, resources, grade entry |

---

## 13. Risks & Mitigation Strategies
| Risk | Impact | Probability | Mitigation | Contingency |
| --- | --- | --- | --- | --- |
| Missing `.env` vars | High | Medium | Deployment checklist, validation script | Emergency rollback |
| Data migration issues | High | Medium | Dry runs, validation, backups | Manual entry / restore |
| User adoption resistance | Medium | Medium | Training, champions, feedback loops | Phased rollout |
| SQLite in production | High | High (if unaddressed) | Mandate Postgres for prod | Emergency DB conversion |
| Lack of automated tests | Medium | High | Prioritize Sprint 6 testing | Extended UAT |
| Stripe integration complexity | Medium | Low | Sandbox testing, phased rollout | Manual recording |
| Scaling beyond single server | Low | Low | Stateless design, DB tuning | Horizontal scaling plan |
| Security vulnerability | High | Low | Dependency updates, security scans | Incident response plan |
| Developer unavailability | Medium | Medium | Knowledge sharing, documentation | Cross-training, contractors |

---

## 14. Open Questions & Decisions
1. **Payment/Fee Scope:** Sprint 10 or separate epic? *(Decision by Sprint 6 end.)*
2. **Advanced Reporting Needs:** Beyond attendance analytics? *(Decision during Sprint 7 planning.)*
3. **Student Self-Service Timing:** Include in v2.0? *(Decision for Sprint 9 planning.)*
4. **CI/CD Automation:** Invest now or later? *(Decision in Sprint 6.)*
5. **Multi-language Support:** Required for stakeholder base? *(Decision in Sprint 8.)*
6. **Native Mobile Apps:** Necessary vs responsive web? *(Decision in Sprint 10.)*

---

## 15. Appendices
### 15.1 Glossary
- **Admission Number:** Unique identifier (`YEAR-SEQUENCE`).
- **ASGI/WSGI:** Python web server interfaces.
- **Cookiecutter-Django:** Best-practice Django template.
- **CRUD:** Create, Read, Update, Delete.
- **RBAC:** Role-Based Access Control.
- **MoSCoW:** Must/Should/Could/Won’t prioritization.
- **PRD:** Product Requirements Document.
- **Story Points:** Fibonacci-based complexity measure.

### 15.2 References
- Django Documentation – https://docs.djangoproject.com/
- Cookiecutter-Django – https://cookiecutter-django.readthedocs.io/
- PostgreSQL Documentation – https://www.postgresql.org/docs/
- FERPA Guidelines – https://www2.ed.gov/policy/gen/guid/fpco/ferpa/
- WCAG 2.1 – https://www.w3.org/WAI/WCAG21/quickref/
- OWASP Security Best Practices – https://owasp.org/www-project-top-ten/
- Agile User Story Best Practices – https://www.agilealliance.org/glossary/user-stories/

### 15.3 Change Log
| Version | Date | Author | Changes |
| --- | --- | --- | --- |
| 1.0 | 4 Feb 2026 | GitHub Copilot | Initial PRD (Sprint 5) |
| 2.0 | 4 Feb 2026 | Product Team | Comprehensive enhancement with personas, 30+ stories, NFRs, data model, roadmap |

### 15.4 Document Approval
| Role | Name | Signature | Date |
| --- | --- | --- | --- |
| Product Owner |  |  |  |
| Tech Lead |  |  |  |
| School Principal |  |  |  |
| Project Manager |  |  |  |

---
**End of Document**
# Skola Platform – Product Requirements Document (PRD)

**Version:** 1.0  
**Date:** 4 Feb 2026  
**Author:** GitHub Copilot (GPT-5.1-Codex)  
**Sprint Covered:** Sprint 5 (Mon 2 Feb – Fri 13 Feb 2026)

---

## 1. Product Overview
Skola is a lightweight school management platform built on Django with minimal HTML/CSS/JS front-end. It streamlines key academic workflows—authentication, student records, classroom/subject curation, and attendance capture—while enforcing role-aware access. The latest sprint restructured the codebase into a cookiecutter-django layout to improve deployment hygiene and future scalability without changing end-user functionality.

## 2. Objectives & Success Metrics
| Objective | Success Metric | Status |
| --- | --- | --- |
| Ensure modular, environment-driven configuration | Settings split into `config/settings/{base,local,production}.py`; `.env` drives secrets | ✅ |
| Preserve existing functional workflows post-refactor | `python manage.py check` passes; UI flows untouched | ✅ |
| Provide clear deployment artifacts | `.env.example`, requirements matrix, README refresh | ✅ |
| Maintain student/class/attendance capabilities | Manual regression via dev server | ✅ |

## 3. Personas
1. **School Administrator (Admin role)** – Owns user provisioning, classrooms, subjects, and overall oversight. Needs broad CRUD access and dashboards.
2. **Teacher (Teacher role)** – Records attendance, views assigned classes/subjects, sees student rosters.
3. **Staff (Staff role)** – Assists with data entry for students and attendance, but limited administrative privileges.
4. **Student (Student role)** – Read-only access to their profile (future-facing; basics scaffolded via role type).

## 4. Scope
### In Scope (Sprint 5)
- Codebase restructuring to cookiecutter-django conventions.
- Environment-based configuration and dependency matrix.
- Preservation of authentication, student management, classroom/subject, and attendance flows.
- Updated documentation + PRD.

### Out of Scope
- New feature development beyond existing workflows.
- Payment integrations (Stripe request noted for future).
- Mobile-responsive redesign or advanced analytics.
- Docker/CI automation (candidate for next sprint).

## 5. User Stories Delivered
| ID | Story | Acceptance Criteria | Status |
| --- | --- | --- | --- |
| US-101 | Cookiecutter Baseline | Settings in `config/`, modular entrypoints | Done |
| US-102 | Environment & Secrets Management | `.env` read via `django-environ`, `.env.example` committed | Done |
| US-103 | Dependency Matrix | `requirements/base.txt`, `requirements/local.txt`, `requirements/production.txt` | Done |
| US-104 | Operational Entry Points | `manage.py`, ASGI, WSGI target config package | Done |
| US-201 | Authentication & Roles | Custom user model with roles, auth flows intact | Done |
| US-202 | Student Roster Management | Student CRUD views/forms operational | Done |
| US-203 | Classroom & Subject Catalog | Admin can manage classrooms/subjects | Done |
| US-204 | Attendance Tracking & Dashboard | Teachers capture attendance, dashboard shows stats | Done |

## 6. Functional Requirements
### 6.1 Authentication & Authorization
- Custom `accounts.User` extends `AbstractUser` with mandatory `role` field (`ADMIN`, `STAFF`, `TEACHER`, `STUDENT`).
- Login, registration, and role-aware dashboard routing via `accounts.views` (no changes but verified).
- `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL` set in base settings for consistent flow.

### 6.2 Student Management
- CRUD forms/views for `students.Student` with unique `admission_number`, guardian/contact info, status enum, and optional linked `User` account.
- Lists ordered by admission number; search/filter via template controls.

### 6.3 Classroom & Subject Management
- `academics.Classroom` (name, code, homeroom teacher, description) and `academics.Subject` (name, code, classroom, teacher, weekly sessions).
- Relationship enforcement: subjects belong to classrooms; teachers optional.

### 6.4 Attendance Tracking
- `AttendanceRecord` ties `Student`, `Classroom`, optional `Subject`, date, status, notes, and recorder.
- `unique_together(student, subject, date)` prevents duplicate daily entries per subject.
- Views allow teachers/staff to log attendance and review history; dashboard surfaces latest entries.

### 6.5 Configuration & Deployment
- Settings split:
  - `base.py` with shared config, `django-environ` loading, DB via `DATABASE_URL` defaulting to SQLite.
  - `local.py` for debug/dev server defaults.
  - `production.py` enforcing secure defaults (SSL redirect, secure cookies, proxy headers).
- `.env.example` documents required variables; `.env` used locally (ignored from VCS).
- Requirements stack lives in `requirements/` folder with a shim `requirements.txt` for backward compatibility.

## 7. Non-Functional Requirements
- **Security:** Secrets loaded from environment; production settings enforce HTTPS assumptions.
- **Performance:** SQLite remains default; architecture ready for Postgres via `DATABASE_URL` change.
- **Maintainability:** Modular settings, typed properties (`display_name`, `full_name`), and Django best practices facilitate future enhancements.
- **Reliability:** `python manage.py check` must pass before deployment; VS Code task ensures dev server launches consistently.

## 8. System Architecture
```
clients (browser)
    |
Django URLs (config/urls.py)
    |
App Views (accounts, students, academics, attendance)
    |
Django ORM Models (per app)
    |
Database (SQLite by default via DATABASE_URL)
```
Supporting layers: `config/settings` (env aware), templates, static assets, and Forms for validation.

## 9. Data Model Highlights
- **User (`accounts.User`)**: `username`, `email`, password, `role` (enum), `display_name` property.
- **Student (`students.Student`)**: `admission_number` (unique), `user` FK optional, names, DOB, guardian contact, status enum, auto `enrolled_on`.
- **Classroom (`academics.Classroom`)**: `code`, `name`, optional `homeroom_teacher` FK to `User`, description.
- **Subject (`academics.Subject`)**: `code`, `name`, FK to `Classroom`, optional `teacher`, `weekly_sessions`.
- **AttendanceRecord (`attendance.AttendanceRecord`)**: FK to `Student`, `Classroom`, optional `Subject`, `date`, `status` enum, `notes`, `recorded_by`, timestamps.

## 10. Key User Flows
1. **Login & Dashboard** – User hits `/`, authenticates, redirected to dashboard summarizing attendance.
2. **Student CRUD** – Admin navigates to `/students/`, lists students, uses create/edit forms, validations run server-side.
3. **Classroom/Subject Maintenance** – Admin manages entries via `/academics/` endpoints, linking teachers and classrooms.
4. **Attendance Capture** – Teacher selects class/subject, records statuses for each student, entries stored with recorder metadata.

## 11. Release & Launch
- Dev server task (`Run Django Dev Server`) configured in VS Code, confirmed successful run post-refactor.
- README updated with new structure, install steps, and `.env` guidance.
- No migration changes required; existing DB remains compatible.

## 12. Risks & Mitigations
| Risk | Impact | Mitigation |
| --- | --- | --- |
| Missing `.env` variables in production | App fails to boot | Provide `.env.example`, document required vars, add deployment checklist |
| Future Stripe integration touches auth/payment | Compliance & scope creep | Defer to dedicated epic; evaluate `dj-stripe` or Stripe Elements integration |
| Lack of automated tests | Regression risk | Prioritize pytest coverage next sprint, especially for attendance logic |
| SQLite limitations in multi-user prod | Data integrity | Encourage Postgres via `DATABASE_URL` override before production launch |

## 13. Open Questions
1. Should payment/booking (Stripe) be part of the next sprint or a separate epic with new personas (e.g., guardians paying fees)?
2. Is there a requirement for reporting/analytics dashboards beyond attendance snapshots?
3. Do students need self-service access in this release, or is read-only staff entry sufficient?
4. Should we formalize CI/CD (GitHub Actions, Docker) to complement the cookiecutter layout?

---
**Appendix:**
- Source of truth remains the Django app under the new cookiecutter directory structure.
- This PRD captures completed work; future PRDs should extend sections 4–13 with new epics/stories.
