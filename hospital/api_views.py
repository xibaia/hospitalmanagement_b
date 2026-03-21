from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from django.contrib.auth.models import User
from .models import Patient, Doctor, MedicalRecord
from .serializers import (
    PatientRegistrationSerializer,
    PatientLoginSerializer,
    PatientInfoSerializer,
    DoctorListSerializer,
    DoctorLoginSerializer,
    DoctorInfoSerializer,
    MedicalRecordListSerializer,
    MedicalRecordDetailSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def patient_register_api(request):
    """
    患者注册API
    
    请求参数:
    {
        "first_name": "张",
        "last_name": "三",
        "username": "zhangsan",
        "password": "123456",
        "confirm_password": "123456",
        "mobile": "13800138000",
        "address": "北京市朝阳区",
        "symptoms": "头痛",
        "assigned_doctor_id": 1  // 可选，医生的user_id
    }
    
    返回:
    {
        "success": true,
        "message": "注册成功，请等待管理员审核",
        "data": {
            "user_id": 1,
            "username": "zhangsan",
            "full_name": "张三"
        }
    }
    """
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
                    'full_name': f"{user.first_name}{user.last_name}"
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'注册失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'success': False,
        'message': '注册失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def patient_login_api(request):
    """
    患者登录API
    
    请求参数:
    {
        "username": "zhangsan",
        "password": "123456"
    }
    
    返回:
    {
        "success": true,
        "message": "登录成功",
        "data": {
            "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
            "user_info": {
                "user_id": 1,
                "username": "zhangsan",
                "full_name": "张三"
            },
            "patient_info": {
                "id": 1,
                "mobile": "13800138000",
                "address": "北京市朝阳区",
                "symptoms": "头痛",
                "assigned_doctor_name": "李医生",
                "admit_date": "2024-01-01",
                "status": true
            }
        }
    }
    """
    serializer = PatientLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # 获取或创建token
        token, created = Token.objects.get_or_create(user=user)
        
        # 获取患者信息
        try:
            patient = Patient.objects.get(user=user)
            patient_serializer = PatientInfoSerializer(patient)
            
            return Response({
                'success': True,
                'message': '登录成功',
                'data': {
                    'token': token.key,
                    'user_info': {
                        'user_id': user.id,
                        'username': user.username,
                        'full_name': f"{user.first_name}{user.last_name}"
                    },
                    'patient_info': patient_serializer.data
                }
            }, status=status.HTTP_200_OK)
        except Patient.DoesNotExist:
            return Response({
                'success': False,
                'message': '患者信息不存在',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'success': False,
        'message': '登录失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_info_api(request):
    """
    获取当前登录患者信息API
    
    需要在请求头中包含: Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
    
    返回:
    {
        "success": true,
        "message": "获取成功",
        "data": {
            "id": 1,
            "user_info": {
                "id": 1,
                "username": "zhangsan",
                "first_name": "张",
                "last_name": "三",
                "full_name": "张三"
            },
            "address": "北京市朝阳区",
            "mobile": "13800138000",
            "symptoms": "头痛",
            "assignedDoctorId": 1,
            "assigned_doctor_name": "李医生",
            "admitDate": "2024-01-01",
            "status": true
        }
    }
    """
    try:
        patient = Patient.objects.get(user=request.user)
        serializer = PatientInfoSerializer(patient)
        
        return Response({
            'success': True,
            'message': '获取成功',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Patient.DoesNotExist:
        return Response({
            'success': False,
            'message': '患者信息不存在',
            'data': None
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def doctors_list_api(request):
    """
    获取可用医生列表API
    
    返回:
    {
        "success": true,
        "message": "获取成功",
        "data": [
            {
                "id": 1,
                "doctor_name": "李医生",
                "department": "Cardiologist",
                "address": "医院地址",
                "mobile": "13900139000"
            }
        ]
    }
    """
    doctors = Doctor.objects.filter(status=True)
    serializer = DoctorListSerializer(doctors, many=True)
    
    return Response({
        'success': True,
        'message': '获取成功',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def patient_logout_api(request):
    """
    患者登出API
    
    需要在请求头中包含: Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
    
    返回:
    {
        "success": true,
        "message": "登出成功",
        "data": null
    }
    """
    try:
        # 删除用户的token
        request.user.auth_token.delete()
        return Response({
            'success': True,
            'message': '登出成功',
            'data': None
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'登出失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_patient_info_api(request):
    """
    更新患者信息API
    
    请求参数:
    {
        "mobile": "13800138001",
        "address": "上海市浦东新区",
        "symptoms": "发烧"
    }
    
    返回:
    {
        "success": true,
        "message": "更新成功",
        "data": {
            // 更新后的患者信息
        }
    }
    """
    try:
        patient = Patient.objects.get(user=request.user)
        
        # 只允许更新特定字段
        allowed_fields = ['mobile', 'address', 'symptoms']
        for field in allowed_fields:
            if field in request.data:
                setattr(patient, field, request.data[field])
        
        patient.save()
        
        serializer = PatientInfoSerializer(patient)
        return Response({
            'success': True,
            'message': '更新成功',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Patient.DoesNotExist:
        return Response({
            'success': False,
            'message': '患者信息不存在',
            'data': None
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'更新失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bind_doctor_api(request):
    """
    患者绑定医生API（通过扫码）
    
    请求参数:
    {
        "doctor_id": 1  // 医生的user_id
    }
    
    返回:
    {
        "success": true,
        "message": "绑定成功",
        "data": {
            "doctor_name": "李医生",
            "department": "Cardiologist"
        }
    }
    """
    try:
        # 获取当前患者
        patient = Patient.objects.get(user=request.user)
        
        # 检查是否已经绑定医生
        if patient.assignedDoctorId:
            return Response({
                'success': False,
                'message': '您已经绑定了医生，无法重复绑定',
                'error_code': 'ALREADY_BOUND',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取医生ID
        doctor_id = request.data.get('doctor_id')
        if not doctor_id:
            return Response({
                'success': False,
                'message': '医生ID不能为空',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证医生是否存在且状态正常
        try:
            doctor = Doctor.objects.get(user_id=doctor_id, status=True)
        except Doctor.DoesNotExist:
            return Response({
                'success': False,
                'message': '医生不存在或已被停用',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 绑定医生
        patient.assignedDoctorId = doctor_id
        patient.save()
        
        return Response({
            'success': True,
            'message': '绑定成功',
            'data': {
                'doctor_name': doctor.get_name,
                'department': doctor.department
            }
        }, status=status.HTTP_200_OK)
        
    except Patient.DoesNotExist:
        return Response({
            'success': False,
            'message': '患者信息不存在',
            'data': None
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'绑定失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== 医生登录 API ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def doctor_login_api(request):
    """
    医生登录API

    请求参数:
    {
        "username": "doctor1",
        "password": "123456"
    }

    返回:
    {
        "success": true,
        "message": "登录成功",
        "data": {
            "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
            "user_info": {
                "user_id": 1,
                "username": "doctor1",
                "full_name": "李医生"
            },
            "doctor_info": {
                "id": 1,
                "mobile": "13900139000",
                "department": "Cardiologist"
            }
        }
    }
    """
    serializer = DoctorLoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data['user']

        # 获取或创建token
        token, created = Token.objects.get_or_create(user=user)

        # 获取医生信息
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
                        'full_name': doctor.get_name
                    },
                    'doctor_info': doctor_serializer.data
                }
            }, status=status.HTTP_200_OK)
        except Doctor.DoesNotExist:
            return Response({
                'success': False,
                'message': '医生信息不存在',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'success': False,
        'message': '登录失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==================== 病历查询 API ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_records_api(request):
    """
    获取当前患者的病历列表API

    需要在请求头中包含: Authorization: Token xxx

    返回:
    {
        "success": true,
        "message": "获取成功",
        "data": [
            {
                "id": 1,
                "visit_no": "20240321001",
                "check_date": "2024-03-21",
                "visit_type": "charity",
                "visit_type_display": "义诊",
                "patient_name": "张三",
                "doctor_name": "李医生",
                "activity_name": "社区义诊活动",
                "doctor_confirmed": true
            }
        ]
    }
    """
    try:
        # 获取当前患者
        patient = Patient.objects.get(user=request.user)

        # 获取该患者的所有病历
        records = MedicalRecord.objects.filter(patient=patient).order_by('-check_date', '-created_at')

        serializer = MedicalRecordListSerializer(records, many=True)

        return Response({
            'success': True,
            'message': '获取成功',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Patient.DoesNotExist:
        return Response({
            'success': False,
            'message': '患者信息不存在',
            'data': None
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_record_detail_api(request, pk):
    """
    获取病历详情API

    需要在请求头中包含: Authorization: Token xxx

    URL参数: pk - 病历ID

    返回:
    {
        "success": true,
        "message": "获取成功",
        "data": {
            "id": 1,
            "visit_no": "20240321001",
            "check_date": "2024-03-21",
            "visit_type": "charity",
            "visit_type_display": "义诊",
            "patient_name": "张三",
            "doctor_name": "李医生",
            "activity_name": "社区义诊活动",
            "chief_complaint": "牙痛",
            "diagnosis": "龋齿",
            "tooth_findings": [
                {"tooth_number": 16, "finding_type": "caries", "note": "深龋"}
            ],
            "doctor_confirmed": true
        }
    }
    """
    try:
        # 获取当前患者
        patient = Patient.objects.get(user=request.user)

        # 获取指定病历（只能查看自己的）
        record = MedicalRecord.objects.get(id=pk, patient=patient)

        serializer = MedicalRecordDetailSerializer(record)

        return Response({
            'success': True,
            'message': '获取成功',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Patient.DoesNotExist:
        return Response({
            'success': False,
            'message': '患者信息不存在',
            'data': None
        }, status=status.HTTP_404_NOT_FOUND)
    except MedicalRecord.DoesNotExist:
        return Response({
            'success': False,
            'message': '病历不存在或无权查看',
            'data': None
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)