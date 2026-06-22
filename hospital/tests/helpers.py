from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.utils import timezone
from rest_framework.authtoken.models import Token

from hospital.models import (
    Activity,
    Appointment,
    Doctor,
    MedicalRecord,
    Patient,
    PatientDischargeDetails,
    Station,
    ToothFinding,
    Volunteer,
)


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


def create_appointment(
    patient,
    doctor,
    description="Follow-up appointment",
    status=True,
):
    return Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        patientName=patient.get_name,
        doctorName=doctor.get_name,
        description=description,
        status=status,
    )


def create_discharge(patient, assigned_doctor_name="未指定", total=460):
    return PatientDischargeDetails.objects.create(
        patient=patient,
        patientName=patient.get_name,
        assignedDoctorName=assigned_doctor_name,
        address=patient.address,
        mobile=patient.mobile,
        symptoms=patient.symptoms,
        admitDate=patient.admitDate,
        releaseDate=timezone.now().date(),
        daySpent=1,
        medicineCost=120,
        roomCharge=200,
        doctorFee=100,
        OtherCharge=40,
        total=total,
    )


def create_station(name="E2E Station", supervisor=None, is_active=True):
    return Station.objects.create(
        name=name,
        address="E2E Station Address",
        latitude=31.2304,
        longitude=121.4737,
        supervisor=supervisor,
        phone="02100000000",
        is_active=is_active,
    )


def create_volunteer(
    username="volunteer",
    password=DEFAULT_PASSWORD,
    status=True,
    **kwargs,
):
    user = create_grouped_user(
        username=username,
        group_name="VOLUNTEER",
        password=password,
        first_name=kwargs.pop("first_name", "Vol"),
        last_name=kwargs.pop("last_name", "Unteer"),
    )
    volunteer = Volunteer.objects.create(
        user=user,
        real_name=kwargs.pop("real_name", "E2E Volunteer"),
        mobile=kwargs.pop("mobile", "13700137000"),
        status=status,
        **kwargs,
    )
    return user, volunteer


def create_tooth_finding(
    record,
    tooth_number=11,
    finding_type="caries",
    note="E2E finding",
):
    return ToothFinding.objects.create(
        record=record,
        tooth_number=tooth_number,
        finding_type=finding_type,
        note=note,
    )
