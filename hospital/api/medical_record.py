from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from hospital.api.common import doctor_required, paginated_response
from hospital.api.permissions import IsDoctor, IsPatient
from hospital.models import MedicalRecord, Patient
from hospital.selectors.medical_record import (
    doctor_records_queryset,
    get_doctor_record,
    get_patient_record,
    patient_records_queryset,
)
from hospital.serializers import MedicalRecordCreateSerializer, MedicalRecordDetailSerializer, MedicalRecordListSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsPatient])
def patient_records_api(request):
    try:
        patient = Patient.objects.get(user=request.user)
        records = patient_records_queryset(patient)
        return paginated_response(request, records, MedicalRecordListSerializer, message='获取成功')
    except Patient.DoesNotExist:
        return Response({'success': False, 'message': '患者信息不存在', 'data': None}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'message': f'获取失败: {str(e)}', 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsPatient])
def patient_record_detail_api(request, pk):
    try:
        patient = Patient.objects.get(user=request.user)
        record = get_patient_record(patient, pk)
        serializer = MedicalRecordDetailSerializer(record)
        return Response({'success': True, 'message': '获取成功', 'data': serializer.data}, status=status.HTTP_200_OK)
    except Patient.DoesNotExist:
        return Response({'success': False, 'message': '患者信息不存在', 'data': None}, status=status.HTTP_404_NOT_FOUND)
    except MedicalRecord.DoesNotExist:
        return Response({'success': False, 'message': '病历不存在或无权查看', 'data': None}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'message': f'获取失败: {str(e)}', 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsDoctor])
@doctor_required
def doctor_records_api(request):
    if request.method == 'GET':
        records = doctor_records_queryset(request.doctor, request.GET.get('activity_id'))
        return paginated_response(request, records, MedicalRecordListSerializer)

    serializer = MedicalRecordCreateSerializer(data=request.data, context={'doctor': request.doctor})
    if serializer.is_valid():
        record = serializer.save(doctor=request.doctor)
        return Response({
            'success': True,
            'message': '病历创建成功',
            'data': {'id': record.id, 'visit_no': record.visit_no},
        }, status=status.HTTP_201_CREATED)
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated, IsDoctor])
@doctor_required
def doctor_record_detail_api(request, pk):
    try:
        record = get_doctor_record(request.doctor, pk)
    except MedicalRecord.DoesNotExist:
        return Response({'success': False, 'message': '病历不存在或无权操作'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = MedicalRecordDetailSerializer(record)
        return Response({'success': True, 'data': serializer.data})

    if record.doctor_confirmed:
        return Response({'success': False, 'message': '病历已确认，无法修改'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = MedicalRecordCreateSerializer(record, data=request.data, partial=True, context={'doctor': request.doctor})
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'message': '病历更新成功'})
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDoctor])
@doctor_required
def doctor_confirm_record_api(request, pk):
    try:
        record = get_doctor_record(request.doctor, pk)
    except MedicalRecord.DoesNotExist:
        return Response({'success': False, 'message': '病历不存在或无权操作'}, status=status.HTTP_404_NOT_FOUND)

    if record.doctor_confirmed:
        return Response({'success': False, 'message': '病历已经确认过了'}, status=status.HTTP_400_BAD_REQUEST)

    record.doctor_confirmed = True
    record.confirmed_at = timezone.now()
    record.save()
    return Response({'success': True, 'message': '病历确认成功', 'data': {'confirmed_at': record.confirmed_at}})
