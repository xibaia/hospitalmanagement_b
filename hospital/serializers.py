from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Patient, Doctor, MedicalRecord, ToothFinding
from django.contrib.auth import authenticate


class PatientRegistrationSerializer(serializers.ModelSerializer):
    """患者注册序列化器"""
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)
    mobile = serializers.CharField(max_length=20)
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
        if obj.doctor:
            try:
                doctor = Doctor.objects.get(user=obj.doctor)
                return doctor.get_name
            except Doctor.DoesNotExist:
                return None
        return None

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
        if obj.doctor:
            try:
                doctor = Doctor.objects.get(user=obj.doctor)
                return doctor.get_name
            except Doctor.DoesNotExist:
                return None
        return None

    def get_activity_name(self, obj):
        return obj.activity.name if obj.activity else None