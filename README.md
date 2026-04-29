# Skola

School management platform for managing students, classes, subjects, attendance, and role-based access. Built on Django 6 with the Cookiecutter-Django project layout, but running the original Skola domain models and views.

## Tech Stack
- Django 6.0 with a custom `accounts.User` model (role aware)
- SQLite for local development (override via `DATABASE_URL`)
- **HTMX** for real-time UI interactions without JavaScript
- Basic HTML/CSS/JS templates (no frontend build pipeline)
- Cookiecutter tooling structure (`pyproject.toml`, `uv.lock`, `.envs/` scaffolding)

## Quick Start
1. **Python environment**
    ```powershell
    py -3.13 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip uv
    ```
2. **Install dependencies**
    ```powershell
    uv pip sync pyproject.toml
    ```
3. **Configure environment**
    - Copy `.env.example` to `.env` (already present) and adjust secrets/DB URLs as needed.
4. **Run database migrations**
    ```powershell
    python manage.py migrate
    ```
5. **(Optional) Seed demo users**
    ```powershell
    python manage.py seed_test_users
    ```
6. **Start the dev server**
    - VS Code: run the `Run Django Dev Server` task (preferred)
    - CLI fallback: `python manage.py runserver`

## Default Accounts
After running `seed_test_users`, the following logins are available (passwords printed in the command output):
- Admin / staff / teacher / student / guardian personas

You can also create your own superuser:
```powershell
python manage.py createsuperuser
```

## Project Structure Highlights
- `accounts`, `students`, `academics`, `attendance`: feature apps migrated from the pre-Cookiecutter project
- `config/settings/`: environment-specific settings (`local`, `production`, `test`). `base.py` mirrors the earlier configuration (SQLite default, Whitenoise, custom user model, Argon2 password hasher)
- `templates/` and `static/`: original UI assets copied under `skola/templates` and `skola/static`

## Features

### Student Management
- CRUD operations for student profiles
- **Bulk CSV Import/Export**: Administrators can import multiple students at once or export existing student data
  - Import preview with validation and error reporting
  - Sample CSV file: `students_import_sample.csv`
  - Required CSV columns: `admission_number`, `first_name`, `last_name`, `date_of_birth` (YYYY-MM-DD), `guardian_name`
    - Optional columns: `current_classroom_code`, `contact_email`, `contact_phone`, `status` (ACTIVE/INACTIVE/GRADUATED)

### Authentication & Authorization
- Role-based access control (Admin, Staff, Teacher, Student, Guardian)
- Custom user model with role field

### Real-time UI with HTMX
- **Live Search**: Instant student search as you type (300ms debounce)
- **Auto-updating Notifications**: Badge updates every 30 seconds without page refresh
- **Inline Delete**: Delete students with confirmation and smooth row removal
- **No JavaScript Required**: All interactions powered by HTML attributes
- 📖 See [`docs/htmx_guide.md`](docs/htmx_guide.md) for implementation details and patterns
- 📋 Quick reference: [`docs/htmx_quickref.md`](docs/htmx_quickref.md)

### Academics
- Class and subject management
- Assignment of teachers to classes/subjects

### Attendance
- Daily attendance tracking per class/subject
- Status tracking (Present, Absent, Late, etc.)
- Guardian notification modes with support for daily attendance digest emails
- **Reports & Analytics**: Comprehensive reporting system with visual charts
  - Filter by date range, classroom, subject, student, and status
  - Daily trend visualization using Chart.js
  - Status distribution pie charts
  - Student absence tracking (identify students with most absences)
  - Export reports to CSV or PDF format
  - Dashboard widget showing 7-day attendance summary

### API & Integrations
- **Core JSON API (`/api/v1/`)** for SIS data access:
    - `GET/POST /api/v1/students/`
    - `GET/PATCH/PUT/DELETE /api/v1/students/<id>/`
    - `GET /api/v1/classrooms/`
    - `GET /api/v1/subjects/`
    - `GET/POST /api/v1/attendance/`
    - `GET/POST /api/v1/grades/`
- **Calendar Sync Feed**: iCalendar export at `/calendar/feed.ics`

## Useful Commands
- `python manage.py check` – configuration validation
- `python manage.py test` – Django test suite
- `python manage.py send_attendance_daily_digest` – sends daily digest emails for guardians in digest mode (defaults to previous day)
- `python manage.py send_attendance_daily_digest --date YYYY-MM-DD` – sends digest for a specific day
- `python manage.py send_attendance_daily_digest --start-date YYYY-MM-DD --end-date YYYY-MM-DD` – sends digest for a specific date range
- `python manage.py shell_plus` – (if you add `django-extensions`) advanced shell

Scheduling note: run the digest command once per day using your scheduler of choice (cron on Linux or Task Scheduler on Windows).

## Deployment Notes
- Configure `DJANGO_ALLOWED_HOSTS`, `DJANGO_SECRET_KEY`, and `DJANGO_DEBUG` via environment variables.
- Switch `DATABASE_URL` to your production PostgreSQL instance.
- Static files are served via Whitenoise; run `python manage.py collectstatic` before deploying.

## Troubleshooting
- **Missing packages**: sync against `pyproject.toml` (`uv pip sync pyproject.toml`).
- **Password hashing errors**: ensure `argon2-cffi` is installed (already pinned in `pyproject.toml`).
- **Port already in use**: stop the running task (`Run Django Dev Server`) before launching another server.

---
MIT Licensed. Refer to `LICENSE` for details.
