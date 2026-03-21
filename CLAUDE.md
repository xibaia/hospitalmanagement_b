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

# Run API tests
python test_api.py

# Docker (alternative)
docker-compose up --build
```

## Architecture

This is a Django 4.2 hospital management system with two parallel interfaces: a traditional web UI and a REST API for WeChat Mini Program / mobile clients.

### Single App Structure

All business logic lives in one app: `hospital/`. The project config is in `hospitalmanagement/`.

### Role-Based Access

Three user roles (Django Groups): **ADMIN**, **DOCTOR**, **PATIENT**. All views use `@login_required` plus custom `is_admin`, `is_doctor`, `is_patient` test functions. Doctors and patients require admin approval (`status` field on model).

### Dual URL Architecture

- `hospitalmanagement/urls.py` — web views: admin/doctor/patient dashboard, appointments, discharge
- `hospital/api_urls.py` — REST API mounted at `/api/`, all endpoints prefixed `/api/patient/` or `/api/doctors/`

### Web vs API Views

- `hospital/views.py` — function-based views rendering HTML templates
- `hospital/api_views.py` — DRF `@api_view` functions returning JSON, using Token authentication

### Key Models (`hospital/models.py`)

- `Doctor` — OneToOne with User, has `department` (choice field) and `status` (approval flag)
- `Patient` — OneToOne with User, has `assignedDoctorId`, `admitDate`, `status`
- `Appointment` — links patientId/doctorId with date and status
- `PatientDischargeDetails` — billing record with room/medicine/doctor charges and total

### PDF Generation

Discharge bills are generated server-side using `xhtml2pdf`. This is triggered from admin views via `hospital/views.py`.

### API Authentication

REST API uses DRF Token authentication. Tokens are created on patient login and returned in the response body. Clients must send `Authorization: Token <token>` header.

### Static & Media Files

`MEDIA_ROOT` is set to `STATIC_DIR` — profile picture uploads go into `static/`. In production, this needs separation.

### Database

SQLite3 (`db.sqlite3`) for development. No fixtures; initial data created via admin UI or `createsuperuser`.
