import base64
from io import BytesIO

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render

from hospital import forms, models
from .common import is_doctor


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor, login_url="doctorlogin")
def doctor_dashboard_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id)
    patientcount=models.Patient.objects.filter(status=True,assignedDoctorId=request.user.id).count()
    appointmentcount=models.Appointment.objects.filter(status=True,doctor=doctor).count()
    patientdischarged=models.PatientDischargeDetails.objects.distinct().filter(assignedDoctorName=doctor.get_name).count()

    appointments=models.Appointment.objects.filter(status=True,doctor=doctor).order_by('-id')
    patientid=[a.patient_id for a in appointments]
    patients=models.Patient.objects.filter(status=True,id__in=patientid).order_by('-id')
    appointments=zip(appointments,patients)
    mydict={
    'patientcount':patientcount,
    'appointmentcount':appointmentcount,
    'patientdischarged':patientdischarged,
    'appointments':appointments,
    'doctor':doctor,
    }
    return render(request,'hospital/doctor_dashboard.html',context=mydict)

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor, login_url="doctorlogin")
def doctor_patient_view(request):
    mydict={
    'doctor':models.Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'hospital/doctor_patient.html',context=mydict)

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor, login_url="doctorlogin")
def doctor_qrcode_view(request):
    # 生成绑定链接，包含医生的 user_id
    doctor_user_id = request.user.id
    # 绑定 API 的基础 URL（小程序可解析该链接并调用 API）
    bind_url = request.build_absolute_uri('/api/patient/bind-doctor/')
    # 将需要的信息编码为 JSON 字符串或查询参数，这里使用最简单的 JSON
    # 由于二维码只承载数据，小程序扫描后自行 POST 数据到 bind_url
    payload = {
        'doctor_id': doctor_user_id,
        'bind_api': bind_url
    }
    import json
    qr_text = json.dumps(payload, ensure_ascii=False)

    # 获取医生对象用于渲染侧边栏头像等
    doctor = models.Doctor.objects.get(user_id=request.user.id)

    img_data_uri = None
    qr_error = None
    try:
        import qrcode  # 延迟导入，避免未安装库时整个站点无法启动
        # 生成二维码
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=6, border=2)
        qr.add_data(qr_text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        img_data_uri = f"data:image/png;base64,{img_base64}"
    except ImportError:
        qr_error = '服务器未安装 qrcode 库，请联系管理员安装：pip install "qrcode[pil]" 或 pip install qrcode pillow'

    context = {
        'qr_image_data_uri': img_data_uri,
        'doctor_user_id': doctor_user_id,
        'bind_url': bind_url,
        'qr_text': qr_text,
        'doctor': doctor,
        'qr_error': qr_error,
    }
    return render(request, 'hospital/doctor_qrcode.html', context)

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor, login_url="doctorlogin")
def doctor_view_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id)
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/doctor_view_patient.html',{'patients':patients,'doctor':doctor})

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor, login_url="doctorlogin")
def search_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    # whatever user write in search box we get in query
    query = request.GET['query']
    patients=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id).filter(Q(symptoms__icontains=query)|Q(user__first_name__icontains=query))
    return render(request,'hospital/doctor_view_patient.html',{'patients':patients,'doctor':doctor})

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor, login_url="doctorlogin")
def doctor_view_discharge_patient_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id)
    dischargedpatients=models.PatientDischargeDetails.objects.filter(assignedDoctorName=doctor.get_name)
    return render(request,'hospital/doctor_view_discharge_patient.html',{'dischargedpatients':dischargedpatients,'doctor':doctor})

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor, login_url="doctorlogin")
def doctor_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/doctor_appointment.html',{'doctor':doctor})

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor, login_url="doctorlogin")
def doctor_view_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.filter(status=True,doctor__user=request.user)
    patientid=[a.patient_id for a in appointments]
    patients=models.Patient.objects.filter(status=True,id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_view_appointment.html',{'appointments':appointments,'doctor':doctor})

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor, login_url="doctorlogin")
def doctor_delete_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.filter(status=True,doctor__user=request.user)
    patientid=[a.patient_id for a in appointments]
    patients=models.Patient.objects.filter(status=True,id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor, login_url="doctorlogin")
def delete_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    doctor=models.Doctor.objects.get(user_id=request.user.id)
    appointments=models.Appointment.objects.filter(status=True,doctor=doctor)
    patientid=[a.patient_id for a in appointments]
    patients=models.Patient.objects.filter(status=True,id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})



#---------------------------------------------------------------------------------
#------------------------ DOCTOR RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------






#---------------------------------------------------------------------------------
#------------------------ PATIENT RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor, login_url="doctorlogin")
def doctor_records_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    records = models.MedicalRecord.objects.filter(doctor=doctor).order_by('-created_at').select_related('patient', 'activity')
    return render(request, 'hospital/doctor_records.html', {
        'doctor': doctor, 'records': records
    })

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor, login_url="doctorlogin")
def doctor_create_record_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    form = forms.MedicalRecordForm()
    formset = forms.ToothFindingFormSet()
    if request.method == 'POST':
        form = forms.MedicalRecordForm(request.POST)
        formset = forms.ToothFindingFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            record = form.save(commit=False)
            record.doctor = doctor
            record.save()
            # 保存牙位 formset
            instances = formset.save(commit=False)
            for instance in instances:
                instance.record = record
                instance.save()
            for obj in formset.deleted_objects:
                obj.delete()
            return redirect('doctor-records')
    return render(request, 'hospital/doctor_create_record.html', {
        'doctor': doctor, 'form': form, 'formset': formset
    })

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor, login_url="doctorlogin")
def doctor_update_record_view(request, pk):
    from django.utils import timezone
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    record = models.MedicalRecord.objects.get(id=pk)
    form = forms.MedicalRecordForm(instance=record)
    formset = forms.ToothFindingFormSet(instance=record)
    if request.method == 'POST':
        form = forms.MedicalRecordForm(request.POST, instance=record)
        formset = forms.ToothFindingFormSet(request.POST, instance=record)
        if form.is_valid() and formset.is_valid():
            r = form.save(commit=False)
            # 首次确认时记录时间
            if r.doctor_confirmed and not record.doctor_confirmed:
                r.confirmed_at = timezone.now()
            r.save()
            formset.save()
            return redirect('doctor-records')
    return render(request, 'hospital/doctor_update_record.html', {
        'doctor': doctor, 'form': form, 'formset': formset, 'record': record
    })


#Developed By : sumit kumar
#facebook : fb.com/sumit.luv


# =========================================================================
# ===================== 病历 MEDICAL RECORD VIEWS (Patient) ================
# =========================================================================
