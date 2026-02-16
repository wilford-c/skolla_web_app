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
