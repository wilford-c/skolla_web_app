Executive Summary
Skola is a modern, unified school management platform built on a Django backend and an HTMX-powered frontend. Its vision is to consolidate all student information, academic management, communications, and financial operations into one intuitive system. By combining server-driven HTML (via Django) with HTMX for dynamic interactions, Skola delivers a responsive, mobile-friendly user experience without a heavy SPA framework
. Key advantages include offline capabilities (PWA/service worker), integrated payments (e.g. EcoCash, SMS), and strict security/compliance. This PRD outlines the product vision, target users, success metrics, core and advanced features, data and API design, deployment strategy, roadmap, and business model.

Product Vision
Integrated Data: Provide a single system of record for student/teacher data, attendance, grades, schedules, fees, and communications. This eliminates fragmented spreadsheets and multiple logins.
User-Centric: Ensure teachers, parents, and administrators can access real-time information (attendance, grades, announcements) from any device.
Offline-Ready: Enable core functions (attendance capture, note-taking) to work without network, syncing automatically when online
.
Scalable & Secure: Build on best practices (Django Cookiecutter) for high availability, data encryption, and compliance (e.g. FERPA/GDPR readiness)
.
Problem Statement
Many schools struggle with disjointed systems: attendance in Excel, billing in third-party tools, and poor parent communication. This causes data silos, errors, and wasted staff time. Skola addresses these gaps by automating routine admin tasks and unifying channels. For example, it centralizes attendance tracking, grade management, and financial reporting – features core SIS/LMS platforms provide
 – and adds modern UX and offline support. Unlike legacy SIS products that often lack per-class attendance or LMS features
, Skola offers granular tracking (per class/lesson, QR codes, geofencing) and built-in learning resources.

Target Users / Personas
School Administrators: Need a 360° view of school operations (enrollment, finances, compliance). They use dashboards for analytics and reports.
Teachers: Use class rosters, attendance entry, gradebook, and messaging tools. They need mobile-friendly UIs (in-class use) and quick grade reporting.
Students: Access timetables, assignments, and progress. They benefit from mobile apps and portals for grades and notifications.
Parents/Guardians: Track child’s attendance, grades, and billing. They receive alerts (SMS/email) and view a parent portal in real time.
Support Staff: (Accountant, Librarian, Nurse) use specialized modules (billing, inventory, health records) to manage school resources.
Success Metrics / KPIs
User Adoption: Number of active teachers, parents, and students using the system daily/week.
Operational Efficiency: Reduction in time spent on registration, attendance logs, and grading (baseline vs post-launch).
Data Accuracy: Decrease in manual errors (e.g. fee reconciliation mismatches).
Engagement: Parent logins and message opens (via portal/SMS/email).
Attendance Compliance: % of attendance entered on time.
Financial Throughput: Total tuition collected online (growth in electronic payments).
System Reliability: Uptime/availability, speed (95th percentile page load time < 1s).
User Satisfaction: Survey scores, support tickets per user.
Core Features (MVP)
User & Role Management: Custom Django user model with roles (Admin, Teacher, Parent, Student). Role-based access control (RBAC) via Django groups/permissions
. Login/auth via Django Allauth (supported by Cookiecutter) for email/username login and optional SSO.
Student Information System: Profiles for Students, Teachers, Parents. Central database for demographics, contact info, enrolment. This covers Class Registration and Student Data as in standard SIS
.
Academic Management: Course/Subject management; class scheduling (assign teachers, times, rooms); timetable. Teachers assign grades and generate report cards. Gradebook supports score entry and auto-calculates totals.
Attendance Tracking: Take attendance per class/period or daily. Options include barcode/QR scanning or geolocation. Automated alerts to parents on absence. Skola supports granular per-class attendance, unlike some legacy SIS
.
Financial Management: Fee/Invoice module to define tuition and other charges. Online payment integration (EcoCash, credit card) with real-time updates. Automated invoicing and receipts. Basic financial reports (outstanding, payments collected). This matches industry needs for invoice and payment processing
.
Parent & Student Portals: Secure portals/mobile views giving parents/students access to grades, attendance, announcements, and fee balances. Message center for teacher-parent communication. Real-time updates ensure everyone is informed
.
Communication: Email/SMS engine for broadcast announcements (exam schedules, events). Built-in templates for report cards and letters. Integrate with SMS providers or services (e.g. Twilio or local SMS API).
Basic Reporting & Analytics: Dashboards with charts (attendance trends, fee collection). Exportable reports (CSV, PDF). At minimum, report cards and attendance summaries.
Advanced Features (Post-MVP)
Offline Sync: Progressive Web App (service worker) to cache assets and form submissions
. Local data storage (e.g. PouchDB) lets teachers take attendance/offline work and sync on reconnect
.
Mobile Apps: Android/iOS apps (or responsive web app) for teachers and parents, with push notifications (Firebase Cloud Messaging).
Learning Management (LMS): File uploads, lesson plans, quiz creation. Integration or basic LMS portal for course materials. (Competitors like SchooledTech highlight built-in LMS as a key differentiator
.)
Multi-Branch Support: Manage multiple campuses/schools in one instance, with data partitioning per location.
Analytics/AI: Predictive insights (e.g. identify absenteeism risk), natural language summaries of performance trends.
Advanced Timetable: Automatic scheduling with conflict checking.
Resource Management: HR/Payroll, Inventory (books, assets).
Localization & Customization: Support multiple languages, school-specific workflows (configurable grading schemes, calendar).
User Flows
Marking Attendance: The teacher logs in, selects “Today’s Classes”, and clicks “Take Attendance”. A list of students appears. Tapping a student toggles present/absent via an HTMX request (snippet example below). The table row updates inline without page reload. Missing attendance triggers automated SMS alerts after class.
Recording Grades: The teacher opens a class’s gradebook, enters scores into a dynamic table, and clicks “Save”. HTMX posts each grade entry or the whole form to the server, updating the status. The report card is auto-generated at term end.
Paying Fees: Parents see an invoice in the portal. They click “Pay” which opens a payment form integrated with EcoCash API. Upon successful payment, the invoice status flips to Paid via an HTMX update, and a receipt email is sent.
Adding a New Student: Admin fills a “New Student” form (personal info, guardians, initial class). On submit, the student record is created, parent notified, and student appears in class roster instantly (via HTML redirect or HTMX insert).
Communication: Admin composes a school-wide announcement in a WYSIWYG editor. They schedule a send; the system dispatches emails/SMS via background jobs. Teachers and parents see the notice in their feeds.
Feature Comparison (Top SIS Competitors)
Platform	Best For	Parent Portal	Attendance	Mobile App	Billing/Fees	LMS Integration
PowerSchool	Large public districts	Yes (limited UI)	Daily attendance	Yes (iOS/Android)	Yes (complex pricing)	Yes
Skyward	K-12 districts	Yes	Daily only	Yes (outdated)	Yes	No
ClassDojo	Elementary engagement	Yes	N/A (focus on rewards)	Yes (modern)	No (free/basic)	No
Gradelink	Small to mid private schools	Yes	Per-class supported	Yes (modern)	Yes (built-in)	Basic
Edsby	Communication-focused	Yes	Limited	Yes (modern)	No (separate SIS)	Moderate

Data from industry reviews
. Skola surpasses many by offering true per-class attendance (vs. daily only), full billing integration (vs. third-party addons), and a modern mobile-first portal. It also includes an LMS module (unlike PowerSchool/Skyward) and robust compliance (GDPR/FERPA) out of the box
.

Data Model Overview
EduCore’s database schema follows normalized design for Student Information Systems
. Key entities include: User (Auth), Student, Teacher, Parent, Class/Section, Enrollment, Subject/Course, AttendanceRecord, Exam/Assessment, GradeRecord, FeeInvoice, Payment, and Notification. For example, the Student table holds personal data and links to a User account or Parent. Enrollment links students to classes. AttendanceRecord ties a student and class to a date and status (present/absent). FeeInvoice and Payment manage billing, with foreign keys to Student. These relate as expected (students enroll in classes; teachers teach subjects; attendance records link to enrollments; invoices link to student accounts). This meets standard SIS schemas which track courses, enrollment, and grades
.

Proposed Database Schema (PostgreSQL)
Below are examples of core tables (fields/type simplified):

Table: UserProfile (from Django auth / cookiecutter)

Field	Type	Description
id	Serial PK	Primary key
username	varchar(150)	Login ID (email or username)
password	varchar	Password hash
email	varchar	Email address
first_name	varchar(30)	First name
last_name	varchar(30)	Last name
role	varchar	Role (admin, teacher, parent, student)

Table: Student

Field	Type	Description
id	Serial PK	Student ID
first_name	varchar(50)	
last_name	varchar(50)	
dob	date	Date of birth
parent_id	int (FK)	References Parent user/profile
class_id	int (FK)	Current primary class/section
enroll_date	date	Enrollment date

Table: Teacher

Field	Type	Description
id	Serial PK	Teacher ID
first_name	varchar(50)	
last_name	varchar(50)	
subject	varchar(100)	Primary subject expertise
email	varchar	Contact email

Table: Class (or Section)

Field	Type	Description
id	Serial PK	Class/section ID
name	varchar	e.g. "Grade 10 – Section A"
teacher_id	int (FK)	Homeroom/lead teacher
schedule	text/json	Recurring time slots/days

Table: Enrollment

Field	Type	Description
id	Serial PK	
student_id	int (FK)	References Student
class_id	int (FK)	References Class
date_joined	date	Date student joined this class

Table: AttendanceRecord

Field	Type	Description
id	Serial PK	
student_id	int (FK)	Student
class_id	int (FK)	Class/section
date	date	Attendance date
status	varchar(10)	e.g. “present”, “absent”, “late”

Table: FeeInvoice

Field	Type	Description
id	Serial PK	
student_id	int (FK)	Billed student
description	varchar	e.g. “Tuition Q1”
amount_due	numeric	In local currency
due_date	date	
status	varchar	e.g. “unpaid”, “paid”

Table: Payment

Field	Type	Description
id	Serial PK	
invoice_id	int (FK)	Related FeeInvoice
student_id	int (FK)	Redundant link to Student
amount_paid	numeric	
date_paid	timestamp	
method	varchar	e.g. “EcoCash”, “CreditCard”

(Other tables like Subject, Exam, GradeRecord, ParentProfile, etc., are similar by pattern.)

API Endpoints (Django/DRF & HTMX)
Skola provides RESTful JSON APIs (via Django REST Framework or Django views) alongside HTML views for HTMX. Key endpoints include:

Endpoint	Method	Purpose / Response
/api/auth/login/	POST	Authenticate user (returns token or session)
/api/students/	GET	List all students (JSON list)
/api/students/	POST	Create new student
/api/students/{id}/	GET	Retrieve student details
/api/students/{id}/	PUT/PATCH	Update student profile
/api/teachers/	GET/POST	List/add teachers
/api/classes/	GET/POST	List/add classes
/api/enrollments/	GET/POST	Manage student-class enrollments
/api/attendance/	GET	List attendance records
/api/attendance/mark/	POST	Mark attendance (accepts student_id, class_id)
/api/fees/	GET/POST	List/add fee invoices
/api/payments/	POST	Record a payment (updates invoice status)
/api/notifications/	POST	Send message/email/SMS to users (bulk)

HTMX-powered pages use similar URLs but return HTML fragments. For example, a POST to /attendance/mark/ might return an updated table row snippet (not JSON) for in-place swapping.

Frontend & HTMX Interactions
The web UI uses Django templates and HTMX (with Alpine.js or Stimulus for minor JS if needed). Core components:

Dashboard: Summary cards (attendance %, upcoming events, alerts). Uses HTMX polling (e.g. hx-trigger="every 30s") for live updates.

Student/Teacher List Views: Data tables with filtering. Pagination links and filters use hx-get to fetch partial table HTML.

Attendance Screen: A class roster table where each student row has a checkbox/button. Example HTMX snippet:

html
Copy
<!-- Mark attendance for a single student (or toggle) -->
<tr id="student-{{ student.id }}">
  <td>{{ student.name }}</td>
  <td>
    <button 
        hx-post="/attendance/mark/{{ student.id }}/" 
        hx-target="closest tr" 
        hx-swap="outerHTML">
      {% if student.is_present %}✓ Present{% else %}Mark{% endif %}
    </button>
  </td>
</tr>
This uses HTMX attributes to POST to the Django view at /attendance/mark/{id}/. The hx-target="closest tr" (nearest <tr>) and hx-swap="outerHTML" replace the entire table row with the response, updating the status inline
.

Payment Processing: On the fees page, each invoice row has a “Pay” button. Example:

html
Copy
<tr id="invoice-{{ invoice.id }}">
  <td>{{ invoice.description }}</td>
  <td>{{ invoice.amount_due }}</td>
  <td>
    <button hx-post="/fees/pay/{{ invoice.id }}/" hx-swap="outerHTML">
      Pay ${{ invoice.amount_due }}
    </button>
  </td>
</tr>
When clicked, it posts to /fees/pay/{id}/, processes the payment via EcoCash/SMS API on the server, and returns an updated row (e.g. showing “Paid”) without a full reload.

Parent Portal: A dropdown lets a parent switch between their children. Using HTMX:

html
Copy
<select hx-get="/parent/{{ parent.id }}/children/" hx-target="#children-div" hx-swap="innerHTML">
  <option>Select a child</option>
  {% for child in parent.children %}<option value="{{ child.id }}">{{ child.name }}</option>{% endfor %}
</select>
<div id="children-div"></div>
When a child is selected, HTMX fetches /parent/{id}/children/ (returns that child’s info panel) and injects it into the page.

HTMX allows us to keep most logic server-side. We respond with HTML fragments (templates or partials) instead of JSON, leveraging Django’s rendering. This “hypermedia” approach avoids a heavy frontend framework
.

Offline & Sync Strategy
Skola follows a Progressive Web App (PWA) model to handle intermittent connectivity. A Service Worker caches core assets (CSS/JS) and an offline landing page
. Key data (e.g. pending attendance or grade entries) are stored in the browser (via IndexedDB or PouchDB
). In the background, the Service Worker intercepts fetch events and uses a cache-first strategy: it serves cached files when offline and queues data submissions for when the network is available
. For example, teachers can mark attendance offline; the entries sync (via a Background Sync or retry logic) once online. This ensures “the app works fully without an internet connection” (offline-first)
.

Authentication & Authorization
Authentication uses Django’s built-in system. We enable Password + Email login with optional two-factor authentication (Django allauth can support MFA). Accounts are tied to roles (using Django’s Groups and Permissions
) so that teachers cannot modify admin data, etc. For instance, only a user in the “Teacher” group has permission to add attendance records. The system uses secure password hashing and supports Single Sign-On (SSO) if needed. Using Django’s auth ensures all CRUD actions respect object-level permissions via has_perm() calls
.

Security & Compliance
Data Encryption: All traffic is HTTPS (Cookiecutter’s default is “secure by default” SSL
). Sensitive data (passwords) are hashed. For stored data, use encrypted DB disks (e.g. AWS RDS encryption). Regular backups with SSL.
OWASP Best Practices: Input validation to prevent SQL injection, use Django’s CSRF protection and built-in XSS/CSRF guards. Parameterized queries (ORM) and Content Security Policy headers.
Audit & Access Logs: All logins and data changes are logged. Role-based views ensure a teacher sees only their classes, etc.
Compliance: The design allows compliance with regulations (FERPA/GDPR). For example, user data export and deletion requests can be handled. Competitors often advertise GDPR-ready features
; Skola includes audit logs and consent tracking for such needs.
Infrastructure Security: Run behind load balancer (AWS ELB/CloudFlare). Use private subnets for DB, secure environments (Cookiecutter dev/prod settings
).
Integrations
EcoCash Payments: We integrate Zimbabwe’s EcoCash via its Developer APIs (mobile money)
. This allows in-app tuition payments and payouts (e.g. staff salaries). (Other options: Stripe/PayPal for international schools.)
SMS Gateway: Integrate with an SMS service (e.g. Twilio, or local SMS APIs) to send notifications for absences, fee reminders, and OTPs.
Email: Use Django AnyMail with providers like Mailgun/SES (Cookiecutter supports this
) for reliable email delivery of reports and alerts.
Push Notifications: Use Firebase Cloud Messaging (web push) or native app push for urgent alerts (e.g. school closures, emergency messages).
LMS & Third-Parties: APIs for exporting/importing data to existing LMS (Canvas, Moodle) or accounting/ERP. For example, sync student data to Google Classroom via APIs.
Deployment & Infrastructure
Skola leverages Docker containers and modern cloud infrastructure. We use the Cookiecutter Django template which provides production-grade Docker Compose setup, Traefik reverse proxy with Let’s Encrypt, and PostgreSQL
. Deployment can be on AWS/Azure/GCP using managed Kubernetes or simple Docker ECS/EKS. For example:

Containerization: One container for Django/Gunicorn, one for Nginx/Traefik, one for Celery worker (background tasks), one for Redis (cache/broker), one for PostgreSQL (or use cloud RDS). Cookiecutter includes examples for AWS ECR/CloudFormation.
CI/CD: GitHub Actions/GitLab CI pipelines run linting, tests (pytest, with 100% coverage out-of-the-box
), then build Docker images, and deploy to staging/production. Images are scanned for vulnerabilities.
Hosting: Options include AWS (EC2/EKS + RDS, or Elastic Beanstalk), Azure App Service, or Heroku (via Cookiecutter Procfile support
). Static/media files can go to S3/GCS with CDN.
Performance & Scalability
Caching: Use Redis (Cookiecutter supports Redis) for caching common queries (student lists, schedules) and Django’s cache framework to reduce DB load.
Load Balancing: Stateless Django servers behind load balancers. Horizontal scaling of web workers and Celery as load increases (e.g. heavy end-of-term reports).
Database: PostgreSQL with indexes on common queries (e.g. attendance by date, student lookup). RDS with read replicas if needed. Cookiecutter advises optimized production DB settings
.
Asynchronous Tasks: Long tasks (CSV exports, sending bulk SMS) run in Celery workers to keep the web responsive.
Static Files: Serve via CDN (e.g. AWS CloudFront).
Testing Strategy
Unit/Integration Tests: Leverage Django’s testing framework and pytest (Cookiecutter sets up pytest) to cover models, views, and API endpoints. Default coverage is 100% on initial codebase
.
Automated Functional Tests: Selenium or Cypress tests for key UI flows (attendance entry, payments).
Security Tests: Use Bandit or SonarQube in CI to check for vulnerabilities. Perform periodic penetration tests.
User Acceptance: Staging environment for pilot testing with real users before production rollout.
Monitoring & Observability
Logging: Structured JSON logs for all requests and errors.
Error Tracking: Integrate Sentry (optional in Cookiecutter) for real-time error alerts and stack traces
.
Metrics: Use Prometheus/Grafana or DataDog to monitor app metrics (CPU, memory, request rate, error rate). Set alerts (e.g. page latency >1s or CPU >80%).
Database Monitoring: Track slow queries, connection pool usage. Cloud DB services offer dashboards.
Roadmap (12 Months)
2026-04-01
2026-05-01
2026-06-01
2026-07-01
2026-08-01
2026-09-01
2026-10-01
2026-11-01
2026-12-01
2027-01-01
2027-02-01
2027-03-01
2027-04-01
2027-05-01
Project Setup & Cookiecutter
Student/Teacher Profiles & Auth
Class, Subject, Enrollment Modules
Attendance & Timetable
Fee Invoicing & Payment Integration
Basic Parent/Student Portal
Mobile Responsive UI + PWA Setup
Service Worker & Offline Sync
SMS/Email Notifications Integration
LMS & File Uploads
Analytics Dashboard & Reporting
Multi-Branch Support & Scaling
QA/Polish & Launch Prep
MVP (Q2 2026)
Beta & Optimization (Q3 2026)
Advanced (Q4 2026 – Q1 2027)
Skola 12-Month Roadmap


Show code
(Dates approximate: 2026-04 start. Overlapping tasks allow parallel development.)

Risks & Mitigations
Data Security Breach: Mitigate by encrypting data-in-transit (SSL/TLS) and at-rest (DB encryption), regular security audits, least-privilege access.
Connectivity/Offline Issues: Our offline-first PWA approach ensures reliability on spotty networks
.
Payment Failures: Implement retry logic, transaction logs, and fallback (manual confirmation). Use proven payment APIs (EcoCash) and confirm all transactions via webhooks.
Adoption Resistance: Provide training and support. Plan iterative rollout (e.g. start with one department) to collect feedback. Dedicated support team as in SchooledTech’s approach
.
Scope Creep: Prioritize MVP features; use the 12-month roadmap to phase work.
Monetization & Pricing
Skola can be sold as SaaS (subscription) or on-premise license. Common models include per-student-per-month pricing (like QuickSchools: ~$0.99–$2.99/user/mo
) or flat per-school tiers. For example, a basic plan might include SIS modules up to 300 students, with add-ons (LMS, advanced analytics, SMS bundle) as paid modules. Enterprise agreements could offer dedicated support, custom integrations, or annual licenses. Additional revenue can come from implementation fees, training, and hosted SMS charges. Competitive pricing will consider market rates: many K-12 SIS charge ~$0.5–$3 per student monthly
.

Next Steps (Implementation)
Sprint 0 (1 week): Set up development environment using Cookiecutter Django with Docker. Establish CI pipeline (tests, linting)
.
Sprint 1 (2 weeks): Implement user auth, profiles for Student/Teacher, group-based permissions. Deliver login/logout, sign-up, and profile CRUD.
Sprint 2 (2 weeks): Build Class and Enrollment modules. Deliver ability to create classes and assign students/teachers.
Sprint 3 (2 weeks): Develop Attendance feature. Deliver attendance form with HTMX updates and parent notification hooks.
Sprint 4 (2 weeks): Create Fee/Invoicing system. Integrate a payment API (EcoCash sandbox) and deliver fee entry, invoice listing, and payment processing.
Sprint 5 (2 weeks): Build Parent/Student portal and communication tools. Deliver basic dashboards and messaging capability.
Sprint 6 (2 weeks): Mobile responsiveness and PWA setup (service worker). Deploy to staging and conduct UAT.
Sprint 7+ (remaining): Implement advanced features (notifications, LMS, analytics) per roadmap. Continuous testing and deployment.
Each sprint delivers a shippable increment (use Scrum ceremonies, backlog grooming). Key milestones include Minimum Viable Product release (after ~3-4 sprints) and Beta Release (post PWA integration).

Sources: Industry guides and documentation informed this plan, including Django and HTMX docs, Cookiecutter Django features
, and school SIS analyses
. These ensure Skola is built on proven foundations and meets modern expectations.