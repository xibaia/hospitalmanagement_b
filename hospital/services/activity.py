from django.db import IntegrityError

from hospital.models import ActivityParticipant


ACTIVITY_STATUS_ACTIVE = 'active'
ACTIVITY_STATUS_ENDED = 'ended'
PARTICIPANT_ROLE_DOCTOR = 'doctor'
PARTICIPANT_ROLE_VOLUNTEER = 'volunteer'


def join_activity(activity, user, requested_role, is_doctor):
    if activity.status != ACTIVITY_STATUS_ACTIVE:
        return False, '该活动不在报名阶段', None

    role = requested_role or PARTICIPANT_ROLE_VOLUNTEER
    if role == PARTICIPANT_ROLE_DOCTOR and not is_doctor:
        role = PARTICIPANT_ROLE_VOLUNTEER

    try:
        _, created = ActivityParticipant.objects.get_or_create(
            activity=activity,
            user=user,
            defaults={'role': role},
        )
    except IntegrityError:
        created = False

    if not created:
        return False, '您已报名该活动', None
    return True, '报名成功', {'role': role}


def leave_activity(activity, user):
    if activity.status == ACTIVITY_STATUS_ENDED:
        return False, '活动已结束，无法取消报名'

    deleted, _ = ActivityParticipant.objects.filter(activity=activity, user=user).delete()
    if deleted:
        return True, '已取消报名'
    return False, '您未报名该活动'
