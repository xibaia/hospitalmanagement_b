from hospital.models import MedicalRecord


def patient_records_queryset(patient):
    return MedicalRecord.objects.filter(
        patient=patient
    ).select_related('doctor', 'activity').order_by('-check_date', '-created_at')


def get_patient_record(patient, pk):
    return MedicalRecord.objects.select_related('doctor', 'activity').get(id=pk, patient=patient)


def doctor_records_queryset(doctor, activity_id=None):
    records = MedicalRecord.objects.filter(
        doctor=doctor
    ).select_related('patient', 'doctor', 'activity').order_by('-check_date', '-created_at')
    if activity_id:
        records = records.filter(activity_id=activity_id)
    return records


def get_doctor_record(doctor, pk):
    return MedicalRecord.objects.select_related('patient', 'doctor', 'activity').get(pk=pk, doctor=doctor)
