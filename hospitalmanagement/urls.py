"""

Developed By : sumit kumar
facebook : fb.com/sumit.luv



"""




from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from hospital import views
from django.contrib.auth.views import LoginView,LogoutView
from django.http import HttpResponse


#-------------FOR ADMIN RELATED URLS
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home_view,name=''),
    # Stub Vite client to avoid 404s when browser or IDE injects HMR client
    path('@vite/client', lambda request: HttpResponse("/* Vite client disabled */ export {};", content_type='application/javascript')),


    path('aboutus', views.aboutus_view),
    path('contactus', views.contactus_view),


    path('adminclick', views.adminclick_view),
    path('doctorclick', views.doctorclick_view),
    path('patientclick', views.patientclick_view),

    path('adminsignup', views.admin_signup_view),
    path('doctorsignup', views.doctor_signup_view,name='doctorsignup'),
    path('patientsignup', views.patient_signup_view),
    
    path('adminlogin', LoginView.as_view(template_name='hospital/adminlogin.html', redirect_authenticated_user=True),name='adminlogin'),
    path('doctorlogin', LoginView.as_view(template_name='hospital/doctorlogin.html', redirect_authenticated_user=True),name='doctorlogin'),
    path('patientlogin', LoginView.as_view(template_name='hospital/patientlogin.html', redirect_authenticated_user=True),name='patientlogin'),


    path('afterlogin', views.afterlogin_view,name='afterlogin'),
    path('logout', LogoutView.as_view(template_name='hospital/index.html'),name='logout'),


    path('admin-dashboard', views.admin_dashboard_view,name='admin-dashboard'),

    path('admin-doctor', views.admin_doctor_view,name='admin-doctor'),
    path('admin-view-doctor', views.admin_view_doctor_view,name='admin-view-doctor'),
    path('delete-doctor-from-hospital/<int:pk>', views.delete_doctor_from_hospital_view,name='delete-doctor-from-hospital'),
    path('update-doctor/<int:pk>', views.update_doctor_view,name='update-doctor'),
    path('admin-add-doctor', views.admin_add_doctor_view,name='admin-add-doctor'),
    path('admin-approve-doctor', views.admin_approve_doctor_view,name='admin-approve-doctor'),
    path('approve-doctor/<int:pk>', views.approve_doctor_view,name='approve-doctor'),
    path('reject-doctor/<int:pk>', views.reject_doctor_view,name='reject-doctor'),
    path('admin-view-doctor-specialisation',views.admin_view_doctor_specialisation_view,name='admin-view-doctor-specialisation'),


    path('admin-patient', views.admin_patient_view,name='admin-patient'),
    path('admin-view-patient', views.admin_view_patient_view,name='admin-view-patient'),
    path('delete-patient-from-hospital/<int:pk>', views.delete_patient_from_hospital_view,name='delete-patient-from-hospital'),
    path('update-patient/<int:pk>', views.update_patient_view,name='update-patient'),
    path('admin-add-patient', views.admin_add_patient_view,name='admin-add-patient'),
    path('admin-approve-patient', views.admin_approve_patient_view,name='admin-approve-patient'),
    path('approve-patient/<int:pk>', views.approve_patient_view,name='approve-patient'),
    path('reject-patient/<int:pk>', views.reject_patient_view,name='reject-patient'),
    path('admin-discharge-patient', views.admin_discharge_patient_view,name='admin-discharge-patient'),
    path('discharge-patient/<int:pk>', views.discharge_patient_view,name='discharge-patient'),
    path('download-pdf/<int:pk>', views.download_pdf_view,name='download-pdf'),


    path('admin-appointment', views.admin_appointment_view,name='admin-appointment'),
    path('admin-view-appointment', views.admin_view_appointment_view,name='admin-view-appointment'),
    path('admin-add-appointment', views.admin_add_appointment_view,name='admin-add-appointment'),
    path('admin-approve-appointment', views.admin_approve_appointment_view,name='admin-approve-appointment'),
    path('approve-appointment/<int:pk>', views.approve_appointment_view,name='approve-appointment'),
    path('reject-appointment/<int:pk>', views.reject_appointment_view,name='reject-appointment'),
]


#---------FOR DOCTOR RELATED URLS-------------------------------------
urlpatterns +=[
    path('doctor-dashboard', views.doctor_dashboard_view,name='doctor-dashboard'),
    path('search', views.search_view,name='search'),

    path('doctor-patient', views.doctor_patient_view,name='doctor-patient'),
    path('doctor-view-patient', views.doctor_view_patient_view,name='doctor-view-patient'),
    path('doctor-view-discharge-patient',views.doctor_view_discharge_patient_view,name='doctor-view-discharge-patient'),

    path('doctor-appointment', views.doctor_appointment_view,name='doctor-appointment'),
    path('doctor-view-appointment', views.doctor_view_appointment_view,name='doctor-view-appointment'),
    path('doctor-delete-appointment',views.doctor_delete_appointment_view,name='doctor-delete-appointment'),
    path('delete-appointment/<int:pk>', views.delete_appointment_view,name='delete-appointment'),
    path('doctor-qrcode', views.doctor_qrcode_view,name='doctor-qrcode'),
]




#---------FOR PATIENT RELATED URLS-------------------------------------
urlpatterns +=[

    path('patient-dashboard', views.patient_dashboard_view,name='patient-dashboard'),
    path('patient-appointment', views.patient_appointment_view,name='patient-appointment'),
    path('patient-book-appointment', views.patient_book_appointment_view,name='patient-book-appointment'),
    path('patient-view-appointment', views.patient_view_appointment_view,name='patient-view-appointment'),
    path('patient-view-doctor', views.patient_view_doctor_view,name='patient-view-doctor'),
    path('searchdoctor', views.search_doctor_view,name='searchdoctor'),
    path('patient-discharge', views.patient_discharge_view,name='patient-discharge'),

]

# -------- 义诊活动 Activity --------
urlpatterns += [
    path('admin-activity', views.admin_activity_view, name='admin-activity'),
    path('admin-add-activity', views.admin_add_activity_view, name='admin-add-activity'),
    path('admin-view-activity/<int:pk>', views.admin_view_activity_view, name='admin-view-activity'),
    path('update-activity/<int:pk>', views.update_activity_view, name='update-activity'),
    path('delete-activity/<int:pk>', views.delete_activity_view, name='delete-activity'),
]

# -------- 志愿者 Volunteer --------
urlpatterns += [
    path('admin-volunteer', views.admin_volunteer_view, name='admin-volunteer'),
    path('admin-add-volunteer', views.admin_add_volunteer_view, name='admin-add-volunteer'),
    path('approve-volunteer/<int:pk>', views.approve_volunteer_view, name='approve-volunteer'),
    path('reject-volunteer/<int:pk>', views.reject_volunteer_view, name='reject-volunteer'),
]

# -------- 站点 Station --------
urlpatterns += [
    path('admin-station', views.admin_station_view, name='admin-station'),
    path('admin-add-station', views.admin_add_station_view, name='admin-add-station'),
    path('update-station/<int:pk>', views.update_station_view, name='update-station'),
    path('delete-station/<int:pk>', views.delete_station_view, name='delete-station'),
]

# -------- 病历 Medical Records --------
urlpatterns += [
    path('admin-medical-records', views.admin_medical_records_view, name='admin-medical-records'),
    path('admin-view-record/<int:pk>', views.admin_view_record_view, name='admin-view-record'),
    path('doctor-records', views.doctor_records_view, name='doctor-records'),
    path('doctor-create-record', views.doctor_create_record_view, name='doctor-create-record'),
    path('doctor-update-record/<int:pk>', views.doctor_update_record_view, name='doctor-update-record'),
    # 患者端病历查看
    path('patient-records', views.patient_records_view, name='patient-records'),
    path('patient-view-record/<int:pk>', views.patient_view_record_view, name='patient-view-record'),
]

# API路由
urlpatterns += [
    path('api/', include('hospital.api_urls')),
]

# 开发环境下提供 media 文件访问（生产环境由 nginx 处理）
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#Developed By : sumit kumar
#facebook : fb.com/sumit.luv
