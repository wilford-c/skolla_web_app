# Skola

Skola is a lightweight school management system built with Django and a minimal HTML/CSS/JS front-end. It focuses on clear workflows for staff members to manage students, classrooms, subjects, and attendance while providing role-aware access control.

The codebase now follows the [cookiecutter-django](https://github.com/cookiecutter/cookiecutter-django) conventions:
- Modular settings split across `config/settings/base.py`, `local.py`, and `production.py`.
- Environment-driven configuration loaded from `.env` (see `.env.example`).
- Structured requirements in `requirements/` for base, local, and production installs.

## Features
- **Authentication & Roles** – Custom `User` model with administrator, staff, teacher, and student roles plus login, registration, and session management.
- **Student Management** – Capture enrollment data, guardians, and contact details; list and create records quickly.
- **Class & Subject Management** – Organize classrooms, assign homeroom teachers, and manage subjects per class.
- **Attendance Tracking** – Record attendance per class/subject with status filters and quick history on the dashboard.
- **Dashboard** – At-a-glance metrics with latest attendance entries.

## Project Structure
```
manage.py
config/
  settings/
    base.py    # shared settings loaded via django-environ
    local.py   # local-only overrides (default when using manage.py)
    production.py
  urls.py      # root URLConf
accounts/      # Custom user model, auth flows, decorators
students/      # Student CRUD views & forms
academics/     # Classrooms & subjects
attendance/    # Attendance records & filters
static/        # Base CSS
templates/     # HTML templates grouped by app
requirements/  # base/local/production requirement sets
```

## Getting Started
1. **Install dependencies**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements/local.txt
   ```
2. **Create your environment file**
   ```bash
   copy .env.example .env  # PowerShell: Copy-Item .env.example .env
   ```
   Update values as needed (secret key, database URL, allowed hosts, timezone).
3. **Apply migrations**
   ```bash
   python manage.py migrate
   ```
4. **Create a superuser (optional but recommended)**
   ```bash
   python manage.py createsuperuser
   ```
5. **Run the dev server**
   ```bash
   python manage.py runserver
   ```
6. Visit http://127.0.0.1:8000/ and start managing your school data.

### Seed demo accounts
Quickly create one user for every role (admin, staff, teacher, student) so you can preview the role-based dashboards:

```bash
python manage.py seed_test_users  # add --password=myPass to override the default
```

| Username | Role        | Password        |
| -------- | ----------- | ----------------|
| admin    | Administrator | `SkolaTest123!` |
| staff    | Staff       | `SkolaTest123!` |
| teacher  | Teacher     | `SkolaTest123!` |
| student  | Student     | `SkolaTest123!` |

Running the command again resets the same password and keeps profile details in sync, so it is safe to re-run whenever you need to refresh your test data.

## Testing & Checks
Run the Django system checks before committing:
```bash
python manage.py check
```

## Future Enhancements
- Bulk student import/export
- Attendance analytics (per class/term)
- Guardian portal with notifications
