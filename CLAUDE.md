# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirement.txt

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Run development server
python manage.py runserver 0.0.0.0:8000

# Create superuser
python manage.py createsuperuser

# Run API tests (standalone script, not Django TestCase)
python test_api.py

# Docker (alternative)
docker-compose up --build

# Utility scripts
python activate_patient.py    # Manually activate a patient account
python fix_doctor_groups.py   # Fix doctor Group membership
```

## Architecture

Django 4.2 hospital management system with two parallel interfaces: a traditional web UI and a REST API for WeChat Mini Program / mobile clients.

### Single App Structure

All business logic lives in one app: `hospital/`. The project config is in `hospitalmanagement/`.

### Role-Based Access

Three user roles (Django Groups): **ADMIN**, **DOCTOR**, **PATIENT**. Web views use `@login_required` + `@user_passes_test(is_admin/is_doctor/is_patient)`. Doctors and patients require admin approval (`status` field on model). Login dispatches to role-specific dashboards via `/afterlogin`.

### Dual URL Architecture

- `hospitalmanagement/urls.py` — web views: admin/doctor/patient dashboard, appointments, discharge
- `hospital/api_urls.py` — REST API mounted at `/api/`, all endpoints prefixed `/api/patient/` or `/api/doctors/`

### Web vs API Views

- `hospital/views.py` — function-based views rendering HTML templates (Session auth)
- `hospital/api_views.py` — DRF `@api_view` functions returning JSON (Token auth)
- `hospital/serializers.py` — DRF serializers for API data transformation
- `hospital/forms.py` — Django forms for web UI

### Key Models (`hospital/models.py`)

- `Doctor` — OneToOne with User, has `department` (choice field), `status` (approval flag), `mobile`, `address`, `profile_pic`
- `Patient` — OneToOne with User, has `assignedDoctorId`, `admitDate`, `symptoms`, `status`
- `Appointment` — links patientId/doctorId with date, description, and status
- `PatientDischargeDetails` — billing record with roomCharge/medicineCost/doctorFee/OtherCharge/total

**Important**: `assignedDoctorId`, `patientId`, `doctorId` are `PositiveIntegerField`, NOT foreign keys. All model relationships are resolved via manual queries (e.g., `Doctor.objects.get(id=assignedDoctorId)`), not Django ORM joins.

### API Endpoints

```
POST /api/patient/register/      # AllowAny — patient registration
POST /api/patient/login/         # AllowAny — returns Token
POST /api/patient/logout/        # Authenticated — deletes Token
GET  /api/patient/info/          # Patient profile
PUT  /api/patient/update/        # Update patient info
GET  /api/doctors/               # List approved doctors
POST /api/patient/bind-doctor/   # Bind doctor (QR code scan scenario)
```

### API Authentication

DRF Token authentication. Tokens created on login, returned in response body. Clients send `Authorization: Token <token>` header. Global default is `IsAuthenticated`; registration/login use `@permission_classes([AllowAny])`.

### PDF Generation

Discharge bills generated server-side using `xhtml2pdf`, triggered from admin views. Templates in `templates/hospital/`.

### Static & Media Files

`MEDIA_ROOT` is set to `STATIC_DIR` — profile picture uploads go into `static/`. In production, this needs separation.

### Database

SQLite3 (`db.sqlite3`) for development. No fixtures; initial data created via admin UI or `createsuperuser`.

### Known Caveats

- `SECRET_KEY` is hardcoded in `settings.py` — must be externalized for production
- `ALLOWED_HOSTS = []` — needs configuration for deployment
- `DEBUG = True` with no environment-based switching
- No `.env` file for sensitive config management
