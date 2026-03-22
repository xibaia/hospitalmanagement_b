from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Patient, Doctor, MedicalRecord, Activity, ActivityParticipant, MedicalHistory, Station
from .serializers import (
    PatientRegistrationSerializer,
    PatientLoginSerializer,
    PatientInfoSerializer,
    DoctorListSerializer,
    DoctorLoginSerializer,
    DoctorInfoSerializer,
    MedicalRecordListSerializer,
    MedicalRecordDetailSerializer,
    ActivityListSerializer,
    ActivityDetailSerializer,
    MyActivitySerializer,
    MedicalHistorySerializer,
    PatientSimpleSerializer,
    PatientDetailSerializer,
    MedicalRecordCreateSerializer,
    StationSerializer,
    PatientUpdateSerializer,
)
from django.db.models import Count, Exists, OuterRef


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
    update_serializer = PatientUpdateSerializer(data=request.data)
    if not update_serializer.is_valid():
        return Response({'success': False, 'message': '参数错误', 'errors': update_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    try:
        patient = Patient.objects.get(user=request.user)

        for field, value in update_serializer.validated_data.items():
            setattr(patient, field, value)
        patient.save()

        serializer = PatientInfoSerializer(patient)
        return Response({'success': True, 'message': '更新成功', 'data': serializer.data})

    except Patient.DoesNotExist:
        return Response({'success': False, 'message': '患者信息不存在', 'data': None}, status=status.HTTP_404_NOT_FOUND)


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

        # select_related 预取关联表，避免 N+1
        records = MedicalRecord.objects.filter(
            patient=patient
        ).select_related('doctor', 'activity').order_by('-check_date', '-created_at')

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

# ==================== 义诊活动 API ====================

# 角色名常量，与 Django Group 名称保持一致
ROLE_DOCTOR = 'DOCTOR'
ROLE_PATIENT = 'PATIENT'

# 活动状态常量，与 Activity.status choices 一致
ACTIVITY_STATUS_ACTIVE = 'active'
ACTIVITY_STATUS_ENDED = 'ended'

# 参与者角色常量，与 ActivityParticipant.role choices 一致
PARTICIPANT_ROLE_DOCTOR = 'doctor'
PARTICIPANT_ROLE_VOLUNTEER = 'volunteer'


def _user_is_doctor(user):
    return user.groups.filter(name=ROLE_DOCTOR).exists()

def _user_is_patient(user):
    return user.groups.filter(name=ROLE_PATIENT).exists()


def _activity_annotate(user):
    """公共 annotate：participant_count + is_joined，列表和详情都用"""
    return {
        'participant_count': Count('participants', distinct=True),
        'is_joined': Exists(
            ActivityParticipant.objects.filter(
                activity=OuterRef('pk'),
                user=user
            )
        )
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activities_list_api(request):
    """
    GET /api/activities/
    - PATIENT：只看 active 状态
    - DOCTOR：可看所有状态（含草稿、已结束）
    用 annotate 避免 N+1 查询
    """
    qs = Activity.objects.annotate(**_activity_annotate(request.user)).order_by('-start_time')

    # 患者只能看进行中的活动
    if not _user_is_doctor(request.user):
        qs = qs.filter(status=ACTIVITY_STATUS_ACTIVE)

    serializer = ActivityListSerializer(qs, many=True, context={'request': request})
    return Response({'success': True, 'data': serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_detail_api(request, pk):
    """
    GET /api/activities/<pk>/
    - DOCTOR：返回完整参与者名单（含姓名）
    - PATIENT：只返回参与人数，不暴露姓名
    """
    try:
        qs = Activity.objects.annotate(**_activity_annotate(request.user))
        # 患者只能查看进行中的活动，医生可查所有状态
        if not _user_is_doctor(request.user):
            qs = qs.filter(status=ACTIVITY_STATUS_ACTIVE)
        activity = qs.get(pk=pk)
    except Activity.DoesNotExist:
        return Response({'success': False, 'message': '活动不存在'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ActivityDetailSerializer(
        activity,
        context={
            'request': request,
            'show_participants': _user_is_doctor(request.user),  # 医生才能看名单
        }
    )
    return Response({'success': True, 'data': serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activity_join_api(request, pk):
    """
    POST /api/activities/<pk>/join/
    Body: {"role": "volunteer"} （医生可传 "doctor"）
    - 活动必须是 active 状态才能报名
    - 医生账户 role 可为 doctor，患者/其他强制为 volunteer
    """
    try:
        activity = Activity.objects.get(pk=pk)
    except Activity.DoesNotExist:
        return Response({'success': False, 'message': '活动不存在'}, status=status.HTTP_404_NOT_FOUND)

    if activity.status != ACTIVITY_STATUS_ACTIVE:
        return Response({'success': False, 'message': '该活动不在报名阶段'}, status=status.HTTP_400_BAD_REQUEST)

    # 非医生账户强制为 volunteer，医生可自选
    role = request.data.get('role', PARTICIPANT_ROLE_VOLUNTEER)
    if role == PARTICIPANT_ROLE_DOCTOR and not _user_is_doctor(request.user):
        role = PARTICIPANT_ROLE_VOLUNTEER

    # get_or_create + 捕获 IntegrityError，解决并发双击导致的 500 问题
    from django.db import IntegrityError
    try:
        _, created = ActivityParticipant.objects.get_or_create(
            activity=activity, user=request.user,
            defaults={'role': role}
        )
    except IntegrityError:
        created = False

    if not created:
        return Response({'success': False, 'message': '您已报名该活动'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'success': True, 'message': '报名成功', 'data': {'role': role}})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def activity_leave_api(request, pk):
    """
    DELETE /api/activities/<pk>/leave/
    只允许在活动 active 状态时取消报名，已结束的活动不可撤销
    """
    try:
        activity = Activity.objects.get(pk=pk)
    except Activity.DoesNotExist:
        return Response({'success': False, 'message': '活动不存在'}, status=status.HTTP_404_NOT_FOUND)

    if activity.status == ACTIVITY_STATUS_ENDED:
        return Response({'success': False, 'message': '活动已结束，无法取消报名'}, status=status.HTTP_400_BAD_REQUEST)

    deleted, _ = ActivityParticipant.objects.filter(activity=activity, user=request.user).delete()
    if deleted:
        return Response({'success': True, 'message': '已取消报名'})
    return Response({'success': False, 'message': '您未报名该活动'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_activities_api(request):
    """
    GET /api/activities/mine/
    返回当前用户报名的所有活动，含报名角色和时间
    """
    participations = ActivityParticipant.objects.filter(
        user=request.user
    ).select_related('activity').order_by('-activity__start_time')

    # 构建 {activity_id: participation} 映射，传入 serializer context
    participation_map = {p.activity_id: p for p in participations}
    activities = [p.activity for p in participations]

    serializer = MyActivitySerializer(
        activities,
        many=True,
        context={'participation_map': participation_map}
    )
    return Response({'success': True, 'data': serializer.data})


# ==================== 医生端 API ====================

def _get_doctor(user):
    """返回已审批的 Doctor 对象，否则返回 None"""
    if not user.groups.filter(name='DOCTOR').exists():
        return None
    try:
        return Doctor.objects.get(user=user, status=True)
    except Doctor.DoesNotExist:
        return None



def doctor_required(func):
    """
    装饰器：验证请求者是已审批医生。
    通过后在 request.doctor 上注入 Doctor 对象，视图无需重复查询。
    """
    from functools import wraps
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        doctor = _get_doctor(request.user)
        if not doctor:
            return Response({'success': False, 'message': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
        request.doctor = doctor
        return func(request, *args, **kwargs)
    return wrapper


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@doctor_required
def doctor_logout_api(request):
    """POST /api/doctor/logout/"""
    try:
        request.user.auth_token.delete()
        return Response({'success': True, 'message': '登出成功', 'data': None})
    except Exception as e:
        return Response({'success': False, 'message': f'登出失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@doctor_required
def doctor_patients_api(request):
    """
    GET /api/doctor/patients/
    查看该医生负责的患者列表，支持 ?search= 按姓名/手机号模糊搜索
    annotate record_count 避免 N+1
    """
    from django.db.models import Q
    qs = Patient.objects.filter(assignedDoctorId=request.user.id)

    search = request.GET.get('search', '').strip()
    if search:
        # 用 Q() 在同一 QuerySet 上过滤，避免 | 拼接丢失条件
        qs = qs.filter(Q(real_name__icontains=search) | Q(mobile__icontains=search))

    patients = qs.annotate(record_count=Count('records')).order_by('-created_at')
    serializer = PatientSimpleSerializer(patients, many=True)
    return Response({'success': True, 'data': serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@doctor_required
def doctor_patient_detail_api(request, pk):
    """
    GET /api/doctor/patients/<pk>/
    查看患者详情（含既往病史、最近5条病历）
    只允许查看：分配给自己的患者 OR 自己有病历记录的患者
    """
    from django.db.models import Q
    # distinct() 防止多条病历关联导致 MultipleObjectsReturned
    patient = Patient.objects.filter(
        Q(pk=pk) & (
            Q(assignedDoctorId=request.user.id) |
            Q(records__doctor=request.doctor)
        )
    ).distinct().first()
    if not patient:
        return Response({'success': False, 'message': '患者不存在或无权查看'}, status=status.HTTP_404_NOT_FOUND)

    serializer = PatientDetailSerializer(patient)
    return Response({'success': True, 'data': serializer.data})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@doctor_required
def doctor_records_api(request):
    """
    GET  /api/doctor/records/       查看自己负责的病历列表，支持 ?activity_id= 过滤
    POST /api/doctor/records/       创建新病历
    """

    if request.method == 'GET':
        records = MedicalRecord.objects.filter(
            doctor=request.doctor
        ).select_related('patient', 'doctor', 'activity').order_by('-check_date', '-created_at')

        activity_id = request.GET.get('activity_id')
        if activity_id:
            records = records.filter(activity_id=activity_id)

        serializer = MedicalRecordListSerializer(records, many=True)
        return Response({'success': True, 'data': serializer.data})

    # POST：创建病历
    serializer = MedicalRecordCreateSerializer(data=request.data)
    if serializer.is_valid():
        record = serializer.save(doctor=request.doctor)
        return Response({
            'success': True,
            'message': '病历创建成功',
            'data': {'id': record.id, 'visit_no': record.visit_no}
        }, status=status.HTTP_201_CREATED)

    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@doctor_required
def doctor_record_detail_api(request, pk):
    """
    GET /api/doctor/records/<pk>/   查看病历详情
    PUT /api/doctor/records/<pk>/   更新病历（已确认的不允许修改）
    """

    try:
        record = MedicalRecord.objects.get(pk=pk, doctor=request.doctor)
    except MedicalRecord.DoesNotExist:
        return Response({'success': False, 'message': '病历不存在或无权操作'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = MedicalRecordDetailSerializer(record)
        return Response({'success': True, 'data': serializer.data})

    # PUT：更新
    if record.doctor_confirmed:
        return Response({'success': False, 'message': '病历已确认，无法修改'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = MedicalRecordCreateSerializer(record, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'message': '病历更新成功'})
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@doctor_required
def doctor_confirm_record_api(request, pk):
    """
    POST /api/doctor/records/<pk>/confirm/
    医生确认病历，设置 doctor_confirmed=True，记录确认时间
    """

    try:
        record = MedicalRecord.objects.get(pk=pk, doctor=request.doctor)
    except MedicalRecord.DoesNotExist:
        return Response({'success': False, 'message': '病历不存在或无权操作'}, status=status.HTTP_404_NOT_FOUND)

    if record.doctor_confirmed:
        return Response({'success': False, 'message': '病历已经确认过了'}, status=status.HTTP_400_BAD_REQUEST)

    record.doctor_confirmed = True
    record.confirmed_at = timezone.now()
    record.save()

    return Response({'success': True, 'message': '病历确认成功', 'data': {'confirmed_at': record.confirmed_at}})


# ==================== 患者病史 API ====================

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def patient_medical_history_api(request):
    """
    GET /api/patient/medical-history/   查看自己的既往病史
    PUT /api/patient/medical-history/   更新既往病史
    """
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return Response({'success': False, 'message': '患者信息不存在'}, status=status.HTTP_404_NOT_FOUND)

    # get_or_create 防止历史数据没有病史记录的情况
    history, _ = MedicalHistory.objects.get_or_create(patient=patient)

    if request.method == 'GET':
        serializer = MedicalHistorySerializer(history)
        return Response({'success': True, 'data': serializer.data})

    serializer = MedicalHistorySerializer(history, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'message': '病史更新成功', 'data': serializer.data})
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# ==================== 站点 API ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stations_list_api(request):
    """GET /api/stations/ 获取启用的义诊站点列表"""
    stations = Station.objects.filter(is_active=True).order_by('name')
    serializer = StationSerializer(stations, many=True)
    return Response({'success': True, 'data': serializer.data})
