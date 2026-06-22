from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from hospital.api.common import (
    activity_annotate,
    paginated_response,
    user_is_doctor,
)
from hospital.models import Activity, ActivityParticipant
from hospital.serializers import ActivityDetailSerializer, ActivityListSerializer, MyActivitySerializer
from hospital.services.activity import ACTIVITY_STATUS_ACTIVE, PARTICIPANT_ROLE_VOLUNTEER, join_activity, leave_activity


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activities_list_api(request):
    qs = Activity.objects.annotate(**activity_annotate(request.user)).order_by('-start_time')
    is_doctor = user_is_doctor(request.user)
    if not is_doctor:
        qs = qs.filter(status=ACTIVITY_STATUS_ACTIVE)
    return paginated_response(request, qs, ActivityListSerializer, context={'request': request})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_detail_api(request, pk):
    is_doctor = user_is_doctor(request.user)
    try:
        qs = Activity.objects.annotate(**activity_annotate(request.user))
        if not is_doctor:
            qs = qs.filter(status=ACTIVITY_STATUS_ACTIVE)
        activity = qs.get(pk=pk)
    except Activity.DoesNotExist:
        return Response({'success': False, 'message': '活动不存在'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ActivityDetailSerializer(
        activity,
        context={'request': request, 'show_participants': is_doctor},
    )
    return Response({'success': True, 'data': serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activity_join_api(request, pk):
    try:
        activity = Activity.objects.get(pk=pk)
    except Activity.DoesNotExist:
        return Response({'success': False, 'message': '活动不存在'}, status=status.HTTP_404_NOT_FOUND)

    success, message, data = join_activity(
        activity,
        request.user,
        request.data.get('role', PARTICIPANT_ROLE_VOLUNTEER),
        user_is_doctor(request.user),
    )
    if not success:
        return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'success': True, 'message': message, 'data': data})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def activity_leave_api(request, pk):
    try:
        activity = Activity.objects.get(pk=pk)
    except Activity.DoesNotExist:
        return Response({'success': False, 'message': '活动不存在'}, status=status.HTTP_404_NOT_FOUND)

    success, message = leave_activity(activity, request.user)
    if success:
        return Response({'success': True, 'message': message})
    return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_activities_api(request):
    participations = ActivityParticipant.objects.filter(
        user=request.user
    ).select_related('activity').order_by('-activity__start_time')
    participation_map = {p.activity_id: p for p in participations}
    activities = [p.activity for p in participations]
    return paginated_response(
        request,
        activities,
        MyActivitySerializer,
        context={'participation_map': participation_map},
    )
