# Sprint Tickets

## Ticket 1: Setup User Registration & Login
- **Summary:** Implement custom authentication with role-based access control for administrators, staff, teachers, and students.
- **User Story:** "As a staff member, I need secure login and role-aware permissions so that only authorized users can manage school data."
- **Acceptance Criteria:**
  - Custom user model with role field.
  - Registration & login forms with validation and feedback.
  - Session handling with remember-me option and logout.
  - Protected dashboard available only to authenticated users.
- **Subtasks:**
  1. Define custom `User` model & migrations.
  2. Build registration/login forms & templates.
  3. Configure auth views, URLs, redirects, and decorators.
  4. Add dashboard widgets showing core metrics.

## Ticket 2: Create Student Management Module
- **Summary:** Provide CRUD flows for managing student profiles and guardian contacts.
- **User Story:** "As an administrator, I need to add and view student profiles so that I can keep enrollment data accurate."
- **Acceptance Criteria:**
  - Student model with admission numbers, guardian info, and statuses.
  - Forms for creating new students with validation.
  - Listing page with key data columns and empty states.
  - Role restrictions so only admins/staff can create records.
- **Subtasks:**
  1. Implement student model, forms, and admin registration.
  2. Develop list and create views with templates.
  3. Wire URLs and navigation links.
  4. Add flash messaging for create actions.

## Ticket 3: Develop Class & Subject Management
- **Summary:** Manage classrooms, homeroom teachers, and subjects per class.
- **User Story:** "As a staff member, I need to organize classes and subjects to keep academic assignments clear."
- **Acceptance Criteria:**
  - Classroom and subject models with teacher references.
  - Forms and listings for both entities.
  - Permissions restricting creation to admin/staff/teachers as appropriate.
  - Navigation entries from the main menu.
- **Subtasks:**
  1. Create classroom & subject models with migrations.
  2. Build forms, list/create views, and templates.
  3. Register in admin and add URL routes.
  4. Surface summary counts on dashboard.

## Ticket 4: Build Attendance Tracking System
- **Summary:** Enable teachers/staff to record daily attendance per class/subject with status tracking.
- **User Story:** "As a teacher, I need to mark student attendance so that records remain up to date."
- **Acceptance Criteria:**
  - Attendance model linking students, classrooms, subjects, and recorder.
  - Form to capture date, status, notes with role checks.
  - Listing view with filters by status and ordering by date.
  - Recent attendance widget on dashboard.
- **Subtasks:**
  1. Implement attendance model, form, and admin interface.
  2. Build create/list views with templates and filters.
  3. Connect URLs and navigation.
  4. Show latest records on dashboard.

---

## This Week's User Stories (Week of February 23, 2026)

## Ticket 5: Bulk Student Import/Export ✅ COMPLETED
- **Summary:** Enable bulk import of student data via CSV and export current student records.
- **User Story:** "As an administrator, I want to import multiple students at once from a CSV file so that I can onboard a new class quickly without manual data entry."
- **Acceptance Criteria:**
  - CSV upload form with file validation and preview functionality. ✅
  - Import process validates data and shows errors before committing. ✅
  - Export feature generates downloadable CSV of all students with filters. ✅
  - Success/error feedback with details on imported records. ✅
  - Only administrators can access import/export functions. ✅
- **Subtasks:**
  1. Create CSV upload form and validation logic. ✅
  2. Build import processor with error handling and dry-run mode. ✅
  3. Implement export view with CSV generation. ✅
  4. Add templates and wire URLs for import/export pages. ✅
  5. Add navigation links and permission checks. ✅
- **Implementation Notes:**
  - Import/export views fully implemented with preview mode
  - CSV validation with detailed error reporting
  - Session-based preview before commit
  - Export with status filtering support
  - All templates and navigation links in place

## Ticket 6: Attendance Reports & Analytics ✅ COMPLETED
- **Summary:** Generate attendance reports showing trends, statistics, and absence patterns.
- **User Story:** "As a teacher, I want to view attendance reports for my class so that I can identify students with frequent absences and intervene early."
- **Acceptance Criteria:**
  - Report page showing attendance statistics by class, student, and date range. ✅
  - Visual charts displaying attendance trends over time. ✅
  - Filter options by class, subject, date range, and attendance status. ✅
  - Export reports to PDF or CSV format. ✅
  - Dashboard widget showing attendance summary metrics. ✅
- **Subtasks:**
  1. Create report model/queries to aggregate attendance data. ✅
  2. Build report view with filtering and date range selection. ✅
  3. Integrate charting library (Chart.js or similar) for visualizations. ✅
  4. Implement PDF/CSV export functionality. ✅
  5. Add dashboard widget and navigation links. ✅
- **Implementation Notes:**
  - Comprehensive reporting system with ReportTemplate model
  - Custom report builder with field selection and grouping
  - CSV, XLSX, and PDF export support via ReportGenerator utility
  - Daily trends with chart data prepared for frontend visualization
  - Template system for saving and reusing report configurations
  - Full admin interface for managing reports

## Ticket 7: Student Performance Tracking ✅ COMPLETED
- **Summary:** Enable teachers to record and track student grades and assessments.
- **User Story:** "As a teacher, I want to record student grades for assessments so that I can track academic progress throughout the term."
- **Acceptance Criteria:**
  - Grade model linking students, subjects, assessment types, and scores. ✅
  - Form to input grades with validation (score ranges, required fields). ✅
  - List view showing grades by student, class, or subject with sorting. ✅
  - Grade calculation for weighted averages and term totals. ✅
  - Role-based access: teachers can enter grades, students can view their own. ✅
- **Subtasks:**
  1. Design grade and assessment models with migrations. ✅
  2. Create forms for grade entry and bulk grade input. ✅
  3. Build list/detail views with filtering and permissions. ✅
  4. Implement grade calculation logic and display. ✅
  5. Add templates, URLs, and student grade view page. ✅
- **Implementation Notes:**
  - Created Assessment model (with type, max_score, weight, date)
  - Created Grade model with automatic percentage and letter grade calculations
  - Implemented 12 views including CRUD, bulk entry, and student grade detail
  - Bulk entry workflow: select assessment → enter grades for all students
  - Student grade view shows weighted averages per subject and overall GPA
  - Registered models in Django admin interface
  - All migrations applied successfully

## Ticket 8: Parent/Guardian Portal Access
- **Summary:** Provide limited portal access for parents to view their child's information.
- **User Story:** "As a parent, I want to log in and view my child's attendance and grades so that I can stay informed about their academic progress."
- **Acceptance Criteria:**
  - Guardian user accounts linked to student profiles.
  - Login redirects guardians to a parent dashboard.
  - Dashboard displays linked student(s) attendance records and grades.
  - Read-only access with no editing permissions.
  - Guardians can only view data for their own children.
- **Subtasks:**
  1. Extend user model or create guardian profiles with student links.
  2. Create parent dashboard view and template.
  3. Implement permission system for guardian role.
  4. Build student selection interface for multi-child guardians.
  5. Add attendance and grade summary displays.

## Ticket 8: Parent/Guardian Portal Access ✅ COMPLETED
- **Summary:** Provide limited portal access for parents to view their child's information.
- **User Story:** "As a parent, I want to log in and view my child's attendance and grades so that I can stay informed about their academic progress."
- **Acceptance Criteria:**
  - Guardian user accounts linked to student profiles. ✅
  - Login redirects guardians to a parent dashboard. ✅
  - Dashboard displays linked student(s) attendance records and grades. ✅
  - Read-only access with no editing permissions. ✅
  - Guardians can only view data for their own children. ✅
- **Subtasks:**
  1. Extend user model or create guardian profiles with student links. ✅
  2. Create parent dashboard view and template. ✅
  3. Implement permission system for guardian role. ✅
  4. Build student selection interface for multi-child guardians. ✅
  5. Add attendance and grade summary displays. ✅
- **Implementation Notes:**
  - Guardian role fully integrated into User model
  - Student model has guardian_user ForeignKey for linking
  - Dedicated guardian dashboard section showing all linked children
  - Each child card displays attendance stats and grade averages
  - Link to view detailed grades per child with permission checks
  - Updated student_grades view to allow guardian access to linked children only
  - Dashboard calculates and displays grade averages for each child

## Ticket 9: Email Notifications for Attendance ✅ COMPLETED
- **Summary:** Automatically send email notifications to guardians when student is marked absent.
- **User Story:** "As a parent, I want to receive email notifications when my child is absent so that I am immediately aware of any attendance issues."
- **Acceptance Criteria:**
  - Email sent to guardian when student marked absent or late. ✅
  - Configurable notification settings (immediate, daily digest, off). ✅
  - Email template with student name, date, status, and reason. ✅
  - Admin settings to enable/disable notifications system-wide. ✅
  - Email delivery logging and error handling. ✅
- **Subtasks:**
  1. Configure email backend in Django settings. ✅
  2. Create email templates for absence notifications. ✅
  3. Implement signal/trigger to send emails on attendance creation. ✅
  4. Build notification preferences model and settings page. ✅
  5. Add admin controls and test email delivery. ✅
  6. Implement background task queue for email sending (Celery optional). ⏭️ (Deferred)
- **Implementation Notes:**
  - NotificationPreference model stores user preferences (immediate, daily digest, off)
  - EmailLog model tracks all sent notifications with status tracking
  - Django signals automatically send emails when attendance is recorded
  - Beautiful HTML and plain text email templates created
  - Guardian settings page allows customization of notification preferences
  - Can choose which statuses to be notified about (absent, late, excused)
  - Option to override email address separate from account email
  - Admin interface for managing preferences and viewing email logs
  - Immediate mode implemented; daily digest can be added via management command
  - All migrations created and applied successfully
