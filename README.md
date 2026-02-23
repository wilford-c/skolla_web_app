# Skola

School management platform for managing students, classes, subjects, attendance, and role-based access. Built on Django 6 with the Cookiecutter-Django project layout, but running the original Skola domain models and views.

## Tech Stack
- Django 6.0 with a custom `accounts.User` model (role aware)
- SQLite for local development (override via `DATABASE_URL`)
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

## Useful Commands
- `python manage.py check` – configuration validation
- `python manage.py test` – Django test suite
- `python manage.py shell_plus` – (if you add `django-extensions`) advanced shell

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
