from hospital import models


def _has_group(user, group_name):
    return bool(user and user.is_authenticated and user.groups.filter(name=group_name).exists())


def is_admin(user):
    return _has_group(user, 'ADMIN')


def has_doctor_role(user):
    return _has_group(user, 'DOCTOR')


def has_patient_role(user):
    return _has_group(user, 'PATIENT')


def is_doctor(user):
    return has_doctor_role(user) and models.Doctor.objects.filter(user=user, status=True).exists()


def is_patient(user):
    return has_patient_role(user) and models.Patient.objects.filter(user=user, status=True).exists()


#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,DOCTOR OR PATIENT
