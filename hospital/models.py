# Developed By: sumit kumar | Extended for dental charity system
# 模型说明：口腔义诊管理系统，包含医生、志愿者、患者、病历、活动、站点等核心模型

from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# ==================== 旧数据兼容（保留） ====================
departments = [
    ('Cardiologist', 'Cardiologist'),
    ('Dermatologists', 'Dermatologists'),
    ('Emergency Medicine Specialists', 'Emergency Medicine Specialists'),
    ('Allergists/Immunologists', 'Allergists/Immunologists'),
    ('Anesthesiologists', 'Anesthesiologists'),
    ('Colon and Rectal Surgeons', 'Colon and Rectal Surgeons'),
]

# ==================== 常量定义 ====================

GENDER_CHOICES = [
    ('M', '男'),
    ('F', '女'),
]

GENDER_CHOICES_WITH_UNKNOWN = [
    ('M', '男'),
    ('F', '女'),
    ('U', '未知'),
]

SPECIALTY_CHOICES = [
    ('restorative', '修复'),
    ('orthodontics', '正畸'),
    ('endodontics', '牙体牙髓'),
    ('implant', '种植'),
    ('periodontics', '牙周'),
    ('pediatric', '儿牙'),
    ('general', '全科'),
]

ACTIVITY_STATUS_CHOICES = [
    ('draft', '草稿'),
    ('active', '进行中'),
    ('ended', '已结束'),
]

PARTICIPANT_ROLE_CHOICES = [
    ('doctor', '医生'),
    ('volunteer', '志愿者'),
]

VISIT_TYPE_CHOICES = [
    ('outpatient', '门诊'),
    ('charity', '义诊'),
    ('referral', '转诊'),
]

MOUTH_OPENING_CHOICES = [
    ('normal', '正常'),
    ('mild_limit', '轻度受限'),
    ('severe_limit', '重度受限'),
]

FINDING_TYPE_CHOICES = [
    ('caries', '龋齿'),
    ('missing', '缺失'),
    ('filling', '充填'),
    ('crown', '冠修复'),
    ('other', '其他'),
]


# ==================== Doctor ====================

# 医生：注册后需管理员审批，可关联多个专科
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    real_name = models.CharField(max_length=20, verbose_name='真实姓名', default='')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='性别', default='M')
    mobile = models.CharField(max_length=20, null=True, blank=True, verbose_name='手机号')
    workplace = models.CharField(max_length=100, blank=True, verbose_name='执业医院')
    introduction = models.TextField(blank=True, verbose_name='个人简介')
    social_roles = models.TextField(blank=True, verbose_name='社会职务')
    status = models.BooleanField(default=False, verbose_name='审批状态')
    profile_pic = models.ImageField(upload_to='profile_pic/DoctorProfilePic/', null=True, blank=True, verbose_name='头像')
    # 保留旧字段兼容旧数据，新业务不再使用
    address = models.CharField(max_length=40, blank=True, default='')
    department = models.CharField(max_length=50, choices=departments, blank=True, default='', verbose_name='科室(旧)')

    # M2M 专科，通过 DoctorSpecialty 中间表
    specialties = models.ManyToManyField('self', through='DoctorSpecialty', symmetrical=False, blank=True)

    @property
    def get_name(self):
        return self.real_name or (self.user.first_name + ' ' + self.user.last_name)

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return f"{self.real_name or self.user.username}"

    class Meta:
        verbose_name = '医生'
        verbose_name_plural = '医生列表'


# ==================== DoctorSpecialty ====================

# 医生专科中间表，一个医生可有多个专科方向
class DoctorSpecialty(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name='医生', related_name='doctor_specialties')
    specialty = models.CharField(max_length=20, choices=SPECIALTY_CHOICES, verbose_name='专科')

    def __str__(self):
        return f"{self.doctor} - {self.get_specialty_display()}"

    class Meta:
        verbose_name = '医生专科'
        verbose_name_plural = '医生专科列表'


# ==================== Volunteer ====================

# 志愿者：参与义诊活动的非医疗人员
class Volunteer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户账号')
    real_name = models.CharField(max_length=20, verbose_name='真实姓名')
    mobile = models.CharField(max_length=20, verbose_name='手机号')
    status = models.BooleanField(default=False, verbose_name='审批状态')
    joined_date = models.DateField(auto_now_add=True, verbose_name='加入日期')

    def __str__(self):
        return f"{self.real_name}({self.user.username})"

    class Meta:
        verbose_name = '志愿者'
        verbose_name_plural = '志愿者列表'


# ==================== Patient ====================

# 患者：可由志愿者/工作人员录入，也可自行注册
class Patient(models.Model):
    # user 允许为空（线下录入场景无需账号）
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='用户账号')
    real_name = models.CharField(max_length=20, default='', verbose_name='真实姓名')
    id_card = models.CharField(max_length=18, blank=True, verbose_name='身份证号')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES_WITH_UNKNOWN, default='U', verbose_name='性别')
    birth_date = models.DateField(null=True, blank=True, verbose_name='出生日期')
    mobile = models.CharField(max_length=20, blank=True, verbose_name='手机号')
    address = models.CharField(max_length=100, blank=True, verbose_name='住址')
    # HL7扩展字段，存储民族/婚姻状况等非标准信息
    extra = models.JSONField(default=dict, blank=True, verbose_name='扩展信息(HL7)')
    created_by = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='registered_patients',
        verbose_name='录入人'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    # 保留旧字段，不删除以兼容旧逻辑
    status = models.BooleanField(default=True, verbose_name='状态')
    symptoms = models.CharField(max_length=100, null=True, blank=True, verbose_name='症状(旧)')
    assignedDoctorId = models.PositiveIntegerField(null=True, blank=True, verbose_name='分配医生ID(旧)')
    admitDate = models.DateField(auto_now=True, verbose_name='入院日期(旧)')
    profile_pic = models.ImageField(upload_to='profile_pic/PatientProfilePic/', null=True, blank=True, verbose_name='头像(旧)')

    @property
    def get_name(self):
        if self.real_name:
            return self.real_name
        if self.user:
            return self.user.first_name + ' ' + self.user.last_name
        return '未知患者'

    @property
    def get_id(self):
        return self.user.id if self.user else self.id

    def __str__(self):
        return self.real_name or (self.user.username if self.user else f'患者#{self.id}')

    class Meta:
        verbose_name = '患者'
        verbose_name_plural = '患者列表'


# ==================== MedicalHistory ====================

# 患者既往病史（OneToOne，随 Patient 创建自动生成）
class MedicalHistory(models.Model):
    patient = models.OneToOneField(
        Patient, on_delete=models.CASCADE,
        related_name='medical_history',
        verbose_name='患者'
    )
    hypertension = models.BooleanField(default=False, verbose_name='高血压')
    heart_disease = models.BooleanField(default=False, verbose_name='心脏病')
    hyperglycemia = models.BooleanField(default=False, verbose_name='高血糖')
    hypoglycemia = models.BooleanField(default=False, verbose_name='低血糖')
    coagulation = models.BooleanField(default=False, verbose_name='凝血障碍')
    medications = models.TextField(blank=True, verbose_name='用药情况')
    allergies = models.TextField(blank=True, verbose_name='过敏史')
    other_history = models.TextField(blank=True, verbose_name='其他病史')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return f"{self.patient} 的病史"

    class Meta:
        verbose_name = '既往病史'
        verbose_name_plural = '既往病史列表'


# Patient 保存后自动创建 MedicalHistory
@receiver(post_save, sender=Patient)
def create_medical_history(sender, instance, created, **kwargs):
    if created:
        MedicalHistory.objects.get_or_create(patient=instance)


# ==================== Activity ====================

# 义诊活动：包含时间地点、负责人、参与人员
class Activity(models.Model):
    name = models.CharField(max_length=100, verbose_name='活动名称')
    location = models.CharField(max_length=100, verbose_name='活动地点')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    description = models.TextField(blank=True, verbose_name='活动描述')
    leader = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='led_activities',
        verbose_name='负责人'
    )
    status = models.CharField(
        max_length=10, choices=ACTIVITY_STATUS_CHOICES,
        default='draft', verbose_name='状态'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return f"{self.name}({self.get_status_display()})"

    class Meta:
        verbose_name = '义诊活动'
        verbose_name_plural = '义诊活动列表'


# ==================== ActivityParticipant ====================

# 活动参与者：记录医生/志愿者参与某次活动
class ActivityParticipant(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name='活动')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    role = models.CharField(max_length=10, choices=PARTICIPANT_ROLE_CHOICES, verbose_name='角色')
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='加入时间')

    def __str__(self):
        return f"{self.user} - {self.activity} [{self.get_role_display()}]"

    class Meta:
        verbose_name = '活动参与者'
        verbose_name_plural = '活动参与者列表'
        unique_together = ('activity', 'user')


# ==================== MedicalRecord ====================

# 病历核心表：记录每次义诊诊疗全流程
class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='records', verbose_name='患者')
    activity = models.ForeignKey(Activity, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='所属活动')
    volunteer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='volunteered_records', verbose_name='接诊志愿者'
    )
    doctor = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='doctor_records', verbose_name='诊疗医生'
    )
    check_date = models.DateField(default=date.today, verbose_name='就诊日期')
    # 格式 YYYYMMDD-NNN，在 save() 中自动生成
    visit_no = models.CharField(max_length=20, unique=True, blank=True, verbose_name='就诊流水号')
    visit_type = models.CharField(
        max_length=10, choices=VISIT_TYPE_CHOICES,
        default='charity', verbose_name='就诊类型'
    )

    # ---- 叙述性文本（问诊记录） ----
    chief_complaint = models.TextField(blank=True, verbose_name='主诉')
    present_illness = models.TextField(blank=True, verbose_name='现病史')
    past_history_note = models.TextField(blank=True, verbose_name='既往史备注')
    auxiliary_exam = models.TextField(blank=True, verbose_name='辅助检查')
    treatment_plan = models.TextField(blank=True, verbose_name='治疗计划')
    informed_consent = models.TextField(blank=True, verbose_name='知情同意')
    treatment_record = models.TextField(blank=True, verbose_name='治疗记录')
    followup_notes = models.TextField(blank=True, verbose_name='复诊备注')

    # ---- 口腔检查结构化字段 ----
    face_symmetry = models.BooleanField(default=True, verbose_name='面部对称')
    has_swelling = models.BooleanField(default=False, verbose_name='是否肿胀')
    mouth_opening = models.CharField(
        max_length=15, choices=MOUTH_OPENING_CHOICES,
        default='normal', verbose_name='开口度'
    )
    extraoral_note = models.TextField(blank=True, verbose_name='口外检查备注')
    has_periodontal = models.BooleanField(default=False, verbose_name='牙周问题')
    mucosa_normal = models.BooleanField(default=True, verbose_name='黏膜正常')
    mucosa_note = models.TextField(blank=True, verbose_name='黏膜备注')
    intraoral_note = models.TextField(blank=True, verbose_name='口内检查备注')
    diagnosis = models.TextField(blank=True, verbose_name='综合诊断')

    # ---- HL7 扩展 ----
    observations = models.JSONField(default=list, verbose_name='观测数据(HL7 OBX)')
    billing = models.JSONField(null=True, blank=True, verbose_name='费用信息(HL7 FT1)')

    # ---- 照片与审核状态 ----
    photos = models.JSONField(default=list, verbose_name='口腔照片路径(最多20张)')
    doctor_confirmed = models.BooleanField(default=False, verbose_name='医生已确认')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='确认时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def save(self, *args, **kwargs):
        # 自动生成就诊流水号，格式 YYYYMMDD-NNN
        if not self.visit_no:
            today = date.today().strftime('%Y%m%d')
            count = MedicalRecord.objects.filter(
                visit_no__startswith=today
            ).count() + 1
            self.visit_no = f"{today}-{count:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.visit_no} - {self.patient}"

    class Meta:
        verbose_name = '病历'
        verbose_name_plural = '病历列表'


# ==================== ToothFinding ====================

# 牙位检查记录：FDI编码，一颗牙可有多行（多种问题）
class ToothFinding(models.Model):
    record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='tooth_findings', verbose_name='病历')
    tooth_number = models.PositiveIntegerField(verbose_name='牙位(FDI编码)')  # 11-48
    finding_type = models.CharField(max_length=10, choices=FINDING_TYPE_CHOICES, verbose_name='问题类型')
    note = models.CharField(max_length=100, blank=True, verbose_name='备注')

    def __str__(self):
        return f"牙{self.tooth_number} - {self.get_finding_type_display()}"

    class Meta:
        verbose_name = '牙位检查'
        verbose_name_plural = '牙位检查列表'


# ==================== Station ====================

# 义诊站点：固定/临时服务点信息
class Station(models.Model):
    name = models.CharField(max_length=100, verbose_name='站点名称')
    address = models.CharField(max_length=200, verbose_name='地址')
    latitude = models.FloatField(null=True, blank=True, verbose_name='纬度')
    longitude = models.FloatField(null=True, blank=True, verbose_name='经度')
    supervisor = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name='负责人'
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '义诊站点'
        verbose_name_plural = '义诊站点列表'


# ==================== 保留原有模型不动 ====================

class Appointment(models.Model):
    patientId = models.PositiveIntegerField(null=True)
    doctorId = models.PositiveIntegerField(null=True)
    patientName = models.CharField(max_length=40, null=True)
    doctorName = models.CharField(max_length=40, null=True)
    appointmentDate = models.DateField(auto_now=True)
    description = models.TextField(max_length=500)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.patientName} -> {self.doctorName} ({self.appointmentDate})"

    class Meta:
        verbose_name = '预约'
        verbose_name_plural = '预约列表'


class PatientDischargeDetails(models.Model):
    patientId = models.PositiveIntegerField(null=True)
    patientName = models.CharField(max_length=40)
    assignedDoctorName = models.CharField(max_length=40)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=True)
    symptoms = models.CharField(max_length=100, null=True)

    admitDate = models.DateField(null=False)
    releaseDate = models.DateField(null=False)
    daySpent = models.PositiveIntegerField(null=False)

    roomCharge = models.PositiveIntegerField(null=False)
    medicineCost = models.PositiveIntegerField(null=False)
    doctorFee = models.PositiveIntegerField(null=False)
    OtherCharge = models.PositiveIntegerField(null=False)
    total = models.PositiveIntegerField(null=False)

    def __str__(self):
        return f"{self.patientName} 出院详情"

    class Meta:
        verbose_name = '出院结算'
        verbose_name_plural = '出院结算列表'
