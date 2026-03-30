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

### Key Models ([models.py](file:///Users/songmingyang/WeChatProjects/hospitalmanagement_b/hospital/models.py))

- `Doctor` — OneToOne with User, has `department` (legacy), `status` (approval flag), `mobile`, `address`, `profile_pic`. Specialized info via `DoctorSpecialty`.
- `Patient` — OneToOne with User, has `assignedDoctorId` (legacy ID), `admitDate` (legacy), `symptoms` (legacy), `status`.
- `MedicalRecord` — Central clinical record, FK to `Patient`, `Doctor`, `Activity`, and `User` (volunteer). Generates unique `visit_no`.
- `Appointment` — links `Patient` / `Doctor` via ForeignKeys.
- `PatientDischargeDetails` — billing record with roomCharge/medicineCost/doctorFee/OtherCharge/total. FK to `Patient`.

**Important**: New relations use ForeignKeys. Older fields like `assignedDoctorId` are kept for legacy compatibility but new logic should prefer `MedicalRecord` associations.

### API Endpoints

Check [API_Documentation.md](file:///Users/songmingyang/WeChatProjects/hospitalmanagement_b/API_Documentation.md) for full v2.0 spec. Key prefixes:
- `/api/patient/` — Registration, info, records, medical history.
- `/api/doctor/` — Login, patients list, records management, confirm diagnosis.
- `/api/activities/` — List, join, leave charity events.
- `/api/doctors/` — Public list of approved doctors.
- `/api/stations/` — List of active screening stations.

### API Authentication & Security

- **Auth**: DRF Token authentication. `Authorization: Token <token>` header.
- **CORS**: Configurable via `.env` (`CORS_ALLOWED_ORIGINS`).
- **Rate Limiting**: Throttling enabled (Anon: 30/min, User: 300/min).
- **Security**: Security headers (XSS, NoSniff, FrameOptions) and HTTPS settings controlled via `.env`.

### Static & Media Files

- `STATIC_URL = '/static/'` — for CSS/JS/images.
- `MEDIA_URL = '/media/'` — for user-uploaded profile pictures and clinical photos.
- `MEDIA_ROOT` is now a separate `media/` directory in project root.

### Database & Config

- **Database**: SQLite3 for development, PostgreSQL for production (switched via `DJANGO_ENV`).
- **Config**: Managed via `python-decouple` (`.env` file). See `.env.example`.

### Known Caveats (Fixed)

- [x] `SECRET_KEY` and sensitive data moved to `.env`.
- [x] `DEBUG` and `ALLOWED_HOSTS` controlled via environment.
- [x] Separate `media/` storage for uploads.
- [x] Rate limiting and security headers implemented.
