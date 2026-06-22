from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from hospital.api.permissions import IsPatient
from hospital.models import Doctor, MedicalHistory, Patient
from hospital.selectors.patient import get_patient_for_user, patient_info_context
from hospital.serializers import (
    MedicalHistorySerializer,
    PatientInfoSerializer,
    PatientLoginSerializer,
    PatientRegistrationSerializer,
    PatientUpdateSerializer,
)


@api_view(['POST'])
@permission_classes([AllowAny])
def patient_register_api(request):
    serializer = PatientRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = serializer.save()
            return Response({
                'success': True,
                'message': '注册成功，请等待管理员审核',
                'data': {
                    'user_id': user.id,
                    'username': user.username,
                    'full_name': f"{user.first_name}{user.last_name}",
                },
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'注册失败: {str(e)}',
                'data': None,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        'success': False,
        'message': '注册失败',
        'errors': serializer.errors,
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def patient_login_api(request):
    serializer = PatientLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        try:
            patient = get_patient_for_user(user)
            patient_serializer = PatientInfoSerializer(patient, context=patient_info_context(patient))
            return Response({
                'success': True,
                'message': '登录成功',
                'data': {
                    'token': token.key,
                    'user_info': {
                        'user_id': user.id,
                        'username': user.username,
                        'full_name': f"{user.first_name}{user.last_name}",
                    },
                    'patient_info': patient_serializer.data,
                },
            }, status=status.HTTP_200_OK)
        except Patient.DoesNotExist:
            return Response({
                'success': False,
                'message': '患者信息不存在',
                'data': None,
            }, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'success': False,
        'message': '登录失败',
        'errors': serializer.errors,
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsPatient])
def patient_info_api(request):
    try:
        patient = get_patient_for_user(request.user)
        serializer = PatientInfoSerializer(patient, context=patient_info_context(patient))
        return Response({
            'success': True,
            'message': '获取成功',
            'data': serializer.data,
        }, status=status.HTTP_200_OK)
    except Patient.DoesNotExist:
        return Response({
            'success': False,
            'message': '患者信息不存在',
            'data': None,
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsPatient])
def patient_logout_api(request):
    try:
        request.user.auth_token.delete()
        return Response({
            'success': True,
            'message': '登出成功',
            'data': None,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'登出失败: {str(e)}',
            'data': None,
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsPatient])
def update_patient_info_api(request):
    update_serializer = PatientUpdateSerializer(data=request.data)
    if not update_serializer.is_valid():
        return Response({
            'success': False,
            'message': '参数错误',
            'errors': update_serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        patient = get_patient_for_user(request.user)
        for field, value in update_serializer.validated_data.items():
            setattr(patient, field, value)
        patient.save()

        serializer = PatientInfoSerializer(patient, context=patient_info_context(patient))
        return Response({'success': True, 'message': '更新成功', 'data': serializer.data})
    except Patient.DoesNotExist:
        return Response({'success': False, 'message': '患者信息不存在', 'data': None}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsPatient])
def bind_doctor_api(request):
    try:
        patient = Patient.objects.get(user=request.user)
        if patient.assignedDoctorId:
            return Response({
                'success': False,
                'message': '您已经绑定了医生，无法重复绑定',
                'error_code': 'ALREADY_BOUND',
                'data': None,
            }, status=status.HTTP_400_BAD_REQUEST)

        doctor_id = request.data.get('doctor_id')
        if not doctor_id:
            return Response({
                'success': False,
                'message': '医生ID不能为空',
                'data': None,
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            doctor = Doctor.objects.get(user_id=doctor_id, status=True)
        except Doctor.DoesNotExist:
            return Response({
                'success': False,
                'message': '医生不存在或已被停用',
                'data': None,
            }, status=status.HTTP_404_NOT_FOUND)

        patient.assignedDoctorId = doctor_id
        patient.save()
        return Response({
            'success': True,
            'message': '绑定成功',
            'data': {
                'doctor_name': doctor.get_name,
                'department': doctor.department,
            },
        }, status=status.HTTP_200_OK)
    except Patient.DoesNotExist:
        return Response({
            'success': False,
            'message': '患者信息不存在',
            'data': None,
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'绑定失败: {str(e)}',
            'data': None,
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated, IsPatient])
def patient_medical_history_api(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return Response({'success': False, 'message': '患者信息不存在'}, status=status.HTTP_404_NOT_FOUND)

    history, _ = MedicalHistory.objects.get_or_create(patient=patient)
    if request.method == 'GET':
        serializer = MedicalHistorySerializer(history)
        return Response({'success': True, 'data': serializer.data})

    serializer = MedicalHistorySerializer(history, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'message': '病史更新成功', 'data': serializer.data})
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
