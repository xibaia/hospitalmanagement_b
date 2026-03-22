from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Patient, Doctor, MedicalRecord, ToothFinding, Activity, ActivityParticipant, MedicalHistory, Station
from django.contrib.auth import authenticate


class PatientRegistrationSerializer(serializers.ModelSerializer):
    """患者注册序列化器"""
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)
    mobile = serializers.RegexField(r'^\d{11}$', max_length=11, error_messages={'invalid': '手机号格式不正确，需11位数字'})
    address = serializers.CharField(max_length=40)
    symptoms = serializers.CharField(max_length=100)
    assigned_doctor_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password', 'confirm_password', 
                 'mobile', 'address', 'symptoms', 'assigned_doctor_id']
    
    def validate(self, attrs):
        """验证密码确认"""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("密码和确认密码不匹配")
        return attrs
    
    def validate_username(self, value):
        """验证用户名唯一性"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value
    
    def validate_assigned_doctor_id(self, value):
        """验证分配的医生ID"""
        if value and not Doctor.objects.filter(user_id=value, status=True).exists():
            raise serializers.ValidationError("指定的医生不存在或未激活")
        return value
    
    def create(self, validated_data):
        """创建患者用户和患者信息"""
        # 提取患者相关字段
        mobile = validated_data.pop('mobile')
        address = validated_data.pop('address')
        symptoms = validated_data.pop('symptoms')
        assigned_doctor_id = validated_data.pop('assigned_doctor_id', None)
        validated_data.pop('confirm_password')
        
        # 创建用户
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        
        # 创建患者信息
        patient = Patient.objects.create(
            user=user,
            mobile=mobile,
            address=address,
            symptoms=symptoms,
            assignedDoctorId=assigned_doctor_id,
            status=False  # 默认需要管理员审核
        )
        
        # 添加到患者组
        from django.contrib.auth.models import Group
        patient_group, created = Group.objects.get_or_create(name='PATIENT')
        patient_group.user_set.add(user)
        
        return user


class PatientLoginSerializer(serializers.Serializer):
    """患者登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """验证登录凭据"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("用户名或密码错误")
            
            if not user.is_active:
                raise serializers.ValidationError("用户账户已被禁用")
            
            # 检查是否为患者
            if not user.groups.filter(name='PATIENT').exists():
                raise serializers.ValidationError("该账户不是患者账户")
            
            # 检查患者状态
            try:
                patient = Patient.objects.get(user=user)
                if not patient.status:
                    raise serializers.ValidationError("账户正在等待管理员审核")
            except Patient.DoesNotExist:
                raise serializers.ValidationError("患者信息不存在")
            
            attrs['user'] = user
        else:
            raise serializers.ValidationError("必须提供用户名和密码")
        
        return attrs


class PatientUpdateSerializer(serializers.Serializer):
    """患者信息更新序列化器（含字段校验）"""
    mobile = serializers.RegexField(r'^\d{11}$', required=False, error_messages={'invalid': '手机号格式不正确，需11位数字'})
    address = serializers.CharField(max_length=100, required=False)
    symptoms = serializers.CharField(max_length=100, required=False, allow_blank=True)


class PatientInfoSerializer(serializers.ModelSerializer):
    """患者信息序列化器"""
    user_info = serializers.SerializerMethodField()
    assigned_doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = ['id', 'user_info', 'address', 'mobile', 'symptoms', 
                 'assignedDoctorId', 'assigned_doctor_name', 'admitDate', 'status']
    
    def get_user_info(self, obj):
        """获取用户基本信息"""
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'full_name': obj.get_name
        }
    
    def get_assigned_doctor_name(self, obj):
        """获取分配医生姓名"""
        if obj.assignedDoctorId:
            try:
                doctor = Doctor.objects.get(user_id=obj.assignedDoctorId)
                return doctor.get_name
            except Doctor.DoesNotExist:
                return None
        return None


class DoctorListSerializer(serializers.ModelSerializer):
    """医生列表序列化器"""
    doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = ['id', 'doctor_name', 'department', 'address', 'mobile']
    
    def get_doctor_name(self, obj):
        """获取医生姓名"""
        return obj.get_name


# ==================== 小程序新增序列化器 ====================

class DoctorLoginSerializer(serializers.Serializer):
    """医生登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """验证登录凭据"""
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("用户名或密码错误")

            if not user.is_active:
                raise serializers.ValidationError("用户账户已被禁用")

            # 检查是否为医生
            if not user.groups.filter(name='DOCTOR').exists():
                raise serializers.ValidationError("该账户不是医生账户")

            # 检查医生状态
            try:
                doctor = Doctor.objects.get(user=user)
                if not doctor.status:
                    raise serializers.ValidationError("账户正在等待管理员审核")
            except Doctor.DoesNotExist:
                raise serializers.ValidationError("医生信息不存在")

            attrs['user'] = user
        else:
            raise serializers.ValidationError("必须提供用户名和密码")

        return attrs


class DoctorInfoSerializer(serializers.ModelSerializer):
    """医生信息序列化器"""
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = ['id', 'user_info', 'mobile', 'workplace', 'department',
                 'introduction', 'social_roles', 'status']

    def get_user_info(self, obj):
        """获取用户基本信息"""
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'full_name': obj.get_name
        }


class ToothFindingSerializer(serializers.ModelSerializer):
    """牙位检查序列化器"""
    finding_type_display = serializers.CharField(source='get_finding_type_display', read_only=True)

    class Meta:
        model = ToothFinding
        fields = ['id', 'tooth_number', 'finding_type', 'finding_type_display', 'note']


def _get_doctor_name(doctor):
    """
    公共函数：根据 MedicalRecord.doctor（Doctor 对象）获取医生真实姓名
    调用方需 select_related('doctor') 即可，无需两层 join
    """
    return doctor.get_name if doctor else None


class MedicalRecordListSerializer(serializers.ModelSerializer):
    """病历列表序列化器（简略信息）"""
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    activity_name = serializers.SerializerMethodField()
    visit_type_display = serializers.CharField(source='get_visit_type_display', read_only=True)

    class Meta:
        model = MedicalRecord
        fields = ['id', 'visit_no', 'check_date', 'visit_type', 'visit_type_display',
                 'patient_name', 'doctor_name', 'activity_name', 'doctor_confirmed']

    def get_patient_name(self, obj):
        return obj.patient.get_name if obj.patient else None

    def get_doctor_name(self, obj):
        return _get_doctor_name(obj.doctor)

    def get_activity_name(self, obj):
        return obj.activity.name if obj.activity else None


class MedicalRecordDetailSerializer(serializers.ModelSerializer):
    """病历详情序列化器（完整信息）"""
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    activity_name = serializers.SerializerMethodField()
    visit_type_display = serializers.CharField(source='get_visit_type_display', read_only=True)
    mouth_opening_display = serializers.CharField(source='get_mouth_opening_display', read_only=True)
    tooth_findings = ToothFindingSerializer(many=True, read_only=True)

    class Meta:
        model = MedicalRecord
        fields = ['id', 'visit_no', 'check_date', 'visit_type', 'visit_type_display',
                 'patient_name', 'doctor_name', 'activity_name',
                 # 问诊记录
                 'chief_complaint', 'present_illness', 'past_history_note',
                 'auxiliary_exam', 'treatment_plan', 'informed_consent',
                 'treatment_record', 'followup_notes',
                 # 口腔检查
                 'face_symmetry', 'has_swelling', 'mouth_opening', 'mouth_opening_display',
                 'extraoral_note', 'has_periodontal', 'mucosa_normal', 'mucosa_note',
                 'intraoral_note', 'diagnosis',
                 # 牙位检查
                 'tooth_findings',
                 # 状态
                 'doctor_confirmed', 'confirmed_at', 'created_at']

    def get_patient_name(self, obj):
        return obj.patient.get_name if obj.patient else None

    def get_doctor_name(self, obj):
        return _get_doctor_name(obj.doctor)

    def get_activity_name(self, obj):
        return obj.activity.name if obj.activity else None


# ==================== 义诊活动序列化器 ====================

class ActivityParticipantSerializer(serializers.ModelSerializer):
    """参与者序列化器（仅医生可见）"""
    user_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = ActivityParticipant
        fields = ['id', 'user_name', 'role', 'role_display', 'joined_at']

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class ActivityListSerializer(serializers.ModelSerializer):
    """
    活动列表序列化器
    participant_count / is_joined 依赖 view 层 annotate，不在这里额外查询
    """
    leader_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    # 由 view 层 annotate 注入，直接读取注解字段
    participant_count = serializers.IntegerField(read_only=True)
    is_joined = serializers.BooleanField(read_only=True)

    class Meta:
        model = Activity
        fields = ['id', 'name', 'location', 'start_time', 'end_time',
                  'status', 'status_display', 'leader_name', 'participant_count', 'is_joined']

    def get_leader_name(self, obj):
        return obj.leader.get_full_name() or obj.leader.username if obj.leader else None


class ActivityDetailSerializer(serializers.ModelSerializer):
    """
    活动详情序列化器
    - DOCTOR：返回完整参与者名单（含姓名）
    - PATIENT：隐藏参与者名单，只保留 participant_count
    通过 context['show_participants'] 控制
    """
    leader_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    participants = ActivityParticipantSerializer(many=True, read_only=True)
    # 由 view 层 annotate 注入，与 ActivityListSerializer 保持一致，不额外查询
    participant_count = serializers.IntegerField(read_only=True)
    is_joined = serializers.SerializerMethodField()
    my_role = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = ['id', 'name', 'location', 'start_time', 'end_time',
                  'description', 'status', 'status_display', 'leader_name',
                  'created_at', 'participant_count', 'participants', 'is_joined', 'my_role']

    def get_leader_name(self, obj):
        return obj.leader.get_full_name() or obj.leader.username if obj.leader else None

    def _get_my_participation(self, obj):
        """
        查当前用户的报名记录，结果缓存在 request 上避免重复查询
        is_joined 优先读 view 层 annotate 的值（不查库），my_role 需要查一次
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        cache_attr = f'_act_part_{obj.pk}'
        if not hasattr(request, cache_attr):
            setattr(request, cache_attr,
                    obj.participants.filter(user=request.user).first())
        return getattr(request, cache_attr)

    def get_is_joined(self, obj):
        # 优先用 view 层 annotate 注入的值（零查询），fallback 才查库
        if hasattr(obj, 'is_joined'):
            return obj.is_joined
        return self._get_my_participation(obj) is not None

    def get_my_role(self, obj):
        p = self._get_my_participation(obj)
        return p.role if p else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # 非医生：移除参与者名单，避免隐私泄露
        if not self.context.get('show_participants', False):
            data.pop('participants', None)
        return data


# ==================== 医生端序列化器 ====================

class MedicalHistorySerializer(serializers.ModelSerializer):
    """患者既往病史序列化器（读写通用）"""
    class Meta:
        model = MedicalHistory
        fields = [
            'hypertension', 'heart_disease', 'hyperglycemia', 'hypoglycemia',
            'coagulation', 'medications', 'allergies', 'other_history', 'updated_at'
        ]
        read_only_fields = ['updated_at']


class PatientSimpleSerializer(serializers.ModelSerializer):
    """
    患者简略信息（医生患者列表用）
    record_count 由 view 层 annotate 注入，避免 N+1 查询
    """
    name = serializers.SerializerMethodField()
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    record_count = serializers.IntegerField(default=0, read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'name', 'gender', 'gender_display', 'birth_date', 'mobile', 'record_count', 'created_at']

    def get_name(self, obj):
        return obj.get_name


class PatientDetailSerializer(serializers.ModelSerializer):
    """患者详情（含病史 + 最近5条病历，医生查看用）"""
    name = serializers.SerializerMethodField()
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    medical_history = MedicalHistorySerializer(read_only=True)
    recent_records = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        # 注意：不暴露 id_card（身份证号属于敏感 PII，不对医生开放）
        fields = [
            'id', 'name', 'gender', 'gender_display', 'birth_date',
            'mobile', 'address', 'medical_history', 'recent_records', 'created_at'
        ]

    def get_name(self, obj):
        return obj.get_name

    def get_recent_records(self, obj):
        records = obj.records.select_related('doctor', 'activity').order_by('-check_date')[:5]
        return MedicalRecordListSerializer(records, many=True).data


class ToothFindingWriteSerializer(serializers.ModelSerializer):
    """牙位检查写入序列化器"""
    class Meta:
        model = ToothFinding
        fields = ['tooth_number', 'finding_type', 'note']


class MedicalRecordCreateSerializer(serializers.ModelSerializer):
    """病历创建/更新序列化器（支持批量写入牙位检查）"""
    tooth_findings = ToothFindingWriteSerializer(many=True, required=False)

    class Meta:
        model = MedicalRecord
        fields = [
            'patient', 'activity', 'check_date', 'visit_type',
            'chief_complaint', 'present_illness', 'past_history_note',
            'auxiliary_exam', 'treatment_plan', 'informed_consent',
            'treatment_record', 'followup_notes',
            'face_symmetry', 'has_swelling', 'mouth_opening',
            'extraoral_note', 'has_periodontal', 'mucosa_normal', 'mucosa_note',
            'intraoral_note', 'diagnosis',
            'tooth_findings',
        ]

    def create(self, validated_data):
        tooth_findings_data = validated_data.pop('tooth_findings', [])
        record = MedicalRecord.objects.create(**validated_data)
        for tf in tooth_findings_data:
            ToothFinding.objects.create(record=record, **tf)
        return record

    def update(self, instance, validated_data):
        tooth_findings_data = validated_data.pop('tooth_findings', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        # 有传 tooth_findings 则全量替换
        if tooth_findings_data is not None:
            instance.tooth_findings.all().delete()
            for tf in tooth_findings_data:
                ToothFinding.objects.create(record=instance, **tf)
        return instance


class StationSerializer(serializers.ModelSerializer):
    """义诊站点序列化器"""
    supervisor_name = serializers.SerializerMethodField()

    class Meta:
        model = Station
        fields = ['id', 'name', 'address', 'latitude', 'longitude', 'supervisor_name', 'phone', 'is_active']

    def get_supervisor_name(self, obj):
        if obj.supervisor:
            return obj.supervisor.get_full_name() or obj.supervisor.username
        return None


class MyActivitySerializer(serializers.ModelSerializer):
    """我的报名记录序列化器（含报名角色）"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    # 报名信息由 view 层注入 context['participation_map']
    role = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    joined_at = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = ['id', 'name', 'location', 'start_time', 'end_time',
                  'status', 'status_display', 'role', 'role_display', 'joined_at']

    def _get_participation(self, obj):
        return self.context.get('participation_map', {}).get(obj.pk)

    def get_role(self, obj):
        p = self._get_participation(obj)
        return p.role if p else None

    def get_role_display(self, obj):
        p = self._get_participation(obj)
        return p.get_role_display() if p else None

    def get_joined_at(self, obj):
        p = self._get_participation(obj)
        return p.joined_at if p else None