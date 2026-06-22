from rest_framework.permissions import BasePermission

from hospital.models import Doctor, MedicalRecord, Patient


class IsPatient(BasePermission):
    message = '需要已审批患者账户'

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.groups.filter(name='PATIENT').exists()
            and Patient.objects.filter(user=user, status=True).exists()
        )


class IsDoctor(BasePermission):
    message = '需要已审批医生账户'

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.groups.filter(name='DOCTOR').exists()
            and Doctor.objects.filter(user=user, status=True).exists()
        )


class IsRecordOwnerOrDoctor(BasePermission):
    message = '无权访问该病历'

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, MedicalRecord):
            return False
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if obj.patient and obj.patient.user_id == user.id:
            return True
        return bool(obj.doctor and obj.doctor.user_id == user.id)
