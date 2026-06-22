from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.utils import timezone
from rest_framework.authtoken.models import Token

from hospital.models import Activity, Doctor, MedicalRecord, Patient


DEFAULT_PASSWORD = "pass123456"


def create_grouped_user(username, group_name, password=DEFAULT_PASSWORD, **kwargs):
    user = User.objects.create_user(username=username, password=password, **kwargs)
    group, _ = Group.objects.get_or_create(name=group_name)
    group.user_set.add(user)
    return user


def create_doctor(username="doctor", password=DEFAULT_PASSWORD, status=True, **kwargs):
    user = create_grouped_user(
        username=username,
        group_name="DOCTOR",
        password=password,
        first_name=kwargs.pop("first_name", "Doc"),
        last_name=kwargs.pop("last_name", "Tor"),
    )
    doctor = Doctor.objects.create(
        user=user,
        real_name=kwargs.pop("real_name", f"Dr {username}"),
        mobile=kwargs.pop("mobile", "13900139000"),
        department=kwargs.pop("department", "Cardiologist"),
        status=status,
        **kwargs,
    )
    return user, doctor


def create_patient(
    username="patient",
    password=DEFAULT_PASSWORD,
    status=True,
    assigned_doctor=None,
    **kwargs,
):
    user = create_grouped_user(
        username=username,
        group_name="PATIENT",
        password=password,
        first_name=kwargs.pop("first_name", "Pat"),
        last_name=kwargs.pop("last_name", "Ient"),
    )
    patient = Patient.objects.create(
        user=user,
        real_name=kwargs.pop("real_name", f"Patient {username}"),
        mobile=kwargs.pop("mobile", "13800138000"),
        address=kwargs.pop("address", "Test address"),
        symptoms=kwargs.pop("symptoms", "Test symptoms"),
        assignedDoctorId=assigned_doctor.user_id if assigned_doctor else None,
        status=status,
        **kwargs,
    )
    return user, patient


def auth_headers(user):
    token, _ = Token.objects.get_or_create(user=user)
    return {"HTTP_AUTHORIZATION": f"Token {token.key}"}


def create_activity(name="Community screening", leader=None, status="active"):
    now = timezone.now()
    return Activity.objects.create(
        name=name,
        location="Community clinic",
        start_time=now,
        end_time=now + timedelta(hours=2),
        description="Screening event",
        leader=leader,
        status=status,
    )


def create_record(patient, doctor, activity=None, **kwargs):
    return MedicalRecord.objects.create(
        patient=patient,
        doctor=doctor,
        activity=activity,
        visit_type=kwargs.pop("visit_type", "charity"),
        chief_complaint=kwargs.pop("chief_complaint", "Tooth pain"),
        diagnosis=kwargs.pop("diagnosis", "Caries"),
        **kwargs,
    )
