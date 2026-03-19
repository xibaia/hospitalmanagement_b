from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Patient, Doctor
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