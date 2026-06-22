from functools import wraps

from django.db.models import Count, Exists, OuterRef
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from hospital.models import ActivityParticipant, Doctor, Patient


ROLE_DOCTOR = 'DOCTOR'
ROLE_PATIENT = 'PATIENT'


def paginated_response(request, queryset, serializer_class, context=None, message=None):
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = serializer_class(page if page is not None else queryset, many=True, context=context or {})
    payload = {'success': True, 'data': serializer.data}
    if message:
        payload['message'] = message
    if page is not None:
        payload.update({
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
        })
    return Response(payload)


def user_is_doctor(user):
    return bool(
        user
        and user.is_authenticated
        and user.groups.filter(name=ROLE_DOCTOR).exists()
        and Doctor.objects.filter(user=user, status=True).exists()
    )


def user_is_patient(user):
    return bool(
        user
        and user.is_authenticated
        and user.groups.filter(name=ROLE_PATIENT).exists()
        and Patient.objects.filter(user=user, status=True).exists()
    )


def activity_annotate(user):
    return {
        'participant_count': Count('activityparticipant', distinct=True),
        'is_joined': Exists(
            ActivityParticipant.objects.filter(
                activity=OuterRef('pk'),
                user=user,
            )
        ),
    }


def get_doctor(user):
    if not user.groups.filter(name=ROLE_DOCTOR).exists():
        return None
    try:
        return Doctor.objects.get(user=user, status=True)
    except Doctor.DoesNotExist:
        return None


def doctor_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        doctor = get_doctor(request.user)
        if not doctor:
            return Response({'success': False, 'message': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
        request.doctor = doctor
        return func(request, *args, **kwargs)
    return wrapper
