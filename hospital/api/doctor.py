from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from hospital.api.common import doctor_required, paginated_response
from hospital.api.permissions import IsDoctor
from hospital.models import Doctor
from hospital.selectors.patient import doctor_patients_queryset, get_doctor_visible_patient
from hospital.serializers import DoctorInfoSerializer, DoctorLoginSerializer, PatientDetailSerializer, PatientSimpleSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def doctor_login_api(request):
    serializer = DoctorLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        try:
            doctor = Doctor.objects.get(user=user)
            doctor_serializer = DoctorInfoSerializer(doctor)
            return Response({
                'success': True,
                'message': '登录成功',
                'data': {
                    'token': token.key,
                    'user_info': {
                        'user_id': user.id,
                        'username': user.username,
                        'full_name': doctor.get_name,
                    },
                    'doctor_info': doctor_serializer.data,
                },
            }, status=status.HTTP_200_OK)
        except Doctor.DoesNotExist:
            return Response({'success': False, 'message': '医生信息不存在', 'data': None}, status=status.HTTP_404_NOT_FOUND)

    return Response({'success': False, 'message': '登录失败', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDoctor])
@doctor_required
def doctor_logout_api(request):
    try:
        request.user.auth_token.delete()
        return Response({'success': True, 'message': '登出成功', 'data': None})
    except Exception as e:
        return Response({'success': False, 'message': f'登出失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDoctor])
@doctor_required
def doctor_patients_api(request):
    search = request.GET.get('search', '').strip()
    patients = doctor_patients_queryset(request.doctor, search)
    return paginated_response(request, patients, PatientSimpleSerializer)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDoctor])
@doctor_required
def doctor_patient_detail_api(request, pk):
    patient = get_doctor_visible_patient(request.doctor, pk)
    if not patient:
        return Response({'success': False, 'message': '患者不存在或无权查看'}, status=status.HTTP_404_NOT_FOUND)

    serializer = PatientDetailSerializer(patient)
    return Response({'success': True, 'data': serializer.data})
