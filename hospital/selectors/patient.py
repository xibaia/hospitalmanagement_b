from django.db.models import Count, Q

from hospital.models import Doctor, Patient


def patient_info_context(patient):
    doctor_map = {}
    if patient.assignedDoctorId:
        doctor_map = {
            doctor.user_id: doctor
            for doctor in Doctor.objects.filter(user_id=patient.assignedDoctorId)
        }
    return {'assigned_doctor_map': doctor_map}


def get_patient_for_user(user):
    return Patient.objects.select_related('user').get(user=user)


def doctor_patients_queryset(doctor, search=''):
    queryset = Patient.objects.filter(assignedDoctorId=doctor.user_id)
    if search:
        queryset = queryset.filter(Q(real_name__icontains=search) | Q(mobile__icontains=search))
    return queryset.annotate(record_count=Count('records')).order_by('-created_at')


def get_doctor_visible_patient(doctor, pk):
    return Patient.objects.filter(
        Q(pk=pk) & (
            Q(assignedDoctorId=doctor.user_id) |
            Q(records__doctor=doctor)
        )
    ).distinct().first()
