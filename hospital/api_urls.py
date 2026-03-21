from django.urls import path
from . import api_views

# 患者相关API路由
urlpatterns = [
    # 患者注册
    path('patient/register/', api_views.patient_register_api, name='api-patient-register'),

    # 患者登录
    path('patient/login/', api_views.patient_login_api, name='api-patient-login'),

    # 医生登录
    path('doctor/login/', api_views.doctor_login_api, name='api-doctor-login'),

    # 患者登出
    path('patient/logout/', api_views.patient_logout_api, name='api-patient-logout'),

    # 获取患者信息
    path('patient/info/', api_views.patient_info_api, name='api-patient-info'),

    # 更新患者信息
    path('patient/update/', api_views.update_patient_info_api, name='api-patient-update'),

    # 获取医生列表
    path('doctors/', api_views.doctors_list_api, name='api-doctors-list'),

    # 患者绑定医生（扫码）
    path('patient/bind-doctor/', api_views.bind_doctor_api, name='api-patient-bind-doctor'),

    # 病历查询
    path('patient/records/', api_views.patient_records_api, name='api-patient-records'),
    path('patient/record/<int:pk>/', api_views.patient_record_detail_api, name='api-patient-record-detail'),
]