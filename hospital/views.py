from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required,user_passes_test
from datetime import datetime,timedelta,date
from django.conf import settings
from django.db.models import Q
from io import BytesIO
import base64

# Create your views here.
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/index.html')


#for showing signup/login button for admin(by sumit)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/adminclick.html')


#for showing signup/login button for doctor(by sumit)
def doctorclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/doctorclick.html')


#for showing signup/login button for patient(by sumit)
def patientclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/patientclick.html')




def admin_signup_view(request):
    form=forms.AdminSigupForm()
    if request.method=='POST':
        form=forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.set_password(user.password)
            user.save()
            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)
            return HttpResponseRedirect('adminlogin')
    return render(request,'hospital/adminsignup.html',{'form':form})




def doctor_signup_view(request):
    userForm=forms.DoctorUserForm()
    doctorForm=forms.DoctorForm()
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST)
        doctorForm=forms.DoctorForm(request.POST,request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            doctor=doctorForm.save(commit=False)
            doctor.user=user
            doctor=doctor.save()
            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)
        return HttpResponseRedirect('doctorlogin')
    return render(request,'hospital/doctorsignup.html',context=mydict)


def patient_signup_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient=patient.save()
            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)
        return HttpResponseRedirect('patientlogin')
    return render(request,'hospital/patientsignup.html',context=mydict)






#-----------for checking user is doctor , patient or admin(by sumit)
def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()
def is_doctor(user):
    return user.groups.filter(name='DOCTOR').exists()
def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,DOCTOR OR PATIENT
def afterlogin_view(request):
    if is_admin(request.user):
        return redirect('admin-dashboard')
    elif is_doctor(request.user):
        accountapproval=models.Doctor.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('doctor-dashboard')
        else:
            return render(request,'hospital/doctor_wait_for_approval.html')
    elif is_patient(request.user):
        accountapproval=models.Patient.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('patient-dashboard')
        else:
            return render(request,'hospital/patient_wait_for_approval.html')
    else:
        # 如果用户不属于任何角色，登出用户并重定向到首页
        from django.contrib.auth import logout
        logout(request)
        return redirect('/')








#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_dashboard_view(request):
    #for both table in admin dashboard
    doctors=models.Doctor.objects.all().order_by('-id')
    patients=models.Patient.objects.all().order_by('-id')
    #for three cards
    doctorcount=models.Doctor.objects.all().filter(status=True).count()
    pendingdoctorcount=models.Doctor.objects.all().filter(status=False).count()

    patientcount=models.Patient.objects.all().filter(status=True).count()
    pendingpatientcount=models.Patient.objects.all().filter(status=False).count()

    appointmentcount=models.Appointment.objects.all().filter(status=True).count()
    pendingappointmentcount=models.Appointment.objects.all().filter(status=False).count()

    activitycount = models.Activity.objects.count()
    volunteercount = models.Volunteer.objects.filter(status=True).count()
    pendingvolunteercount = models.Volunteer.objects.filter(status=False).count()
    stationcount = models.Station.objects.filter(is_active=True).count()
    recordcount = models.MedicalRecord.objects.count()

    mydict={
    'doctors':doctors,
    'patients':patients,
    'doctorcount':doctorcount,
    'pendingdoctorcount':pendingdoctorcount,
    'patientcount':patientcount,
    'pendingpatientcount':pendingpatientcount,
    'appointmentcount':appointmentcount,
    'pendingappointmentcount':pendingappointmentcount,
    'activitycount':activitycount,
    'volunteercount':volunteercount,
    'pendingvolunteercount':pendingvolunteercount,
    'stationcount':stationcount,
    'recordcount':recordcount,
    }
    return render(request,'hospital/admin_dashboard.html',context=mydict)


# this view for sidebar click on admin page
@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_doctor_view(request):
    return render(request,'hospital/admin_doctor.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_doctor.html',{'doctors':doctors})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def delete_doctor_from_hospital_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-view-doctor')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def update_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)

    userForm=forms.DoctorUserForm(instance=user)
    doctorForm=forms.DoctorForm(request.FILES,instance=doctor)
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST,instance=user)
        doctorForm=forms.DoctorForm(request.POST,request.FILES,instance=doctor)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            doctor=doctorForm.save(commit=False)
            doctor.status=True
            doctor.save()
            return redirect('admin-view-doctor')
    return render(request,'hospital/admin_update_doctor.html',context=mydict)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_add_doctor_view(request):
    userForm=forms.DoctorUserForm()
    doctorForm=forms.DoctorForm()
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST)
        doctorForm=forms.DoctorForm(request.POST, request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            doctor=doctorForm.save(commit=False)
            doctor.user=user
            doctor.status=True
            doctor.save()

            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-doctor')
    return render(request,'hospital/admin_add_doctor.html',context=mydict)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_approve_doctor_view(request):
    #those whose approval are needed
    doctors=models.Doctor.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_doctor.html',{'doctors':doctors})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def approve_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    doctor.status=True
    doctor.save()
    return redirect(reverse('admin-approve-doctor'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def reject_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-approve-doctor')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_view_doctor_specialisation_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_doctor_specialisation.html',{'doctors':doctors})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_patient_view(request):
    return render(request,'hospital/admin_patient.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_view_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_patient.html',{'patients':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def delete_patient_from_hospital_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-view-patient')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def update_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)

    userForm=forms.PatientUserForm(instance=user)
    patientForm=forms.PatientForm(request.FILES,instance=patient)
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST,instance=user)
        patientForm=forms.PatientForm(request.POST,request.FILES,instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.status=True
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient.save()
            return redirect('admin-view-patient')
    return render(request,'hospital/admin_update_patient.html',context=mydict)





@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_add_patient_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            patient=patientForm.save(commit=False)
            patient.user=user
            patient.status=True
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient.save()

            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-patient')
    return render(request,'hospital/admin_add_patient.html',context=mydict)



#------------------FOR APPROVING PATIENT BY ADMIN----------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_approve_patient_view(request):
    #those whose approval are needed
    patients=models.Patient.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_patient.html',{'patients':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def approve_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    patient.status=True
    patient.save()
    return redirect(reverse('admin-approve-patient'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def reject_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-approve-patient')



#--------------------- FOR DISCHARGING PATIENT BY ADMIN START-------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_discharge_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True)
    return render(request,'hospital/admin_discharge_patient.html',{'patients':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def discharge_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    days=(date.today()-patient.admitDate) #2 days, 0:00:00
    assignedDoctor=models.User.objects.all().filter(id=patient.assignedDoctorId)
    d=days.days # only how many day that is 2
    patientDict={
        'patientId':pk,
        'name':patient.get_name,
        'mobile':patient.mobile,
        'address':patient.address,
        'symptoms':patient.symptoms,
        'admitDate':patient.admitDate,
        'todayDate':date.today(),
        'day':d,
        'assignedDoctorName':assignedDoctor[0].first_name,
    }
    if request.method == 'POST':
        feeDict ={
            'roomCharge':int(request.POST['roomCharge'])*int(d),
            'doctorFee':request.POST['doctorFee'],
            'medicineCost' : request.POST['medicineCost'],
            'OtherCharge' : request.POST['OtherCharge'],
            'total':(int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
        }
        patientDict.update(feeDict)
        #for updating to database patientDischargeDetails (pDD)
        pDD=models.PatientDischargeDetails()
        pDD.patientId=pk
        pDD.patientName=patient.get_name
        pDD.assignedDoctorName=assignedDoctor[0].first_name
        pDD.address=patient.address
        pDD.mobile=patient.mobile
        pDD.symptoms=patient.symptoms
        pDD.admitDate=patient.admitDate
        pDD.releaseDate=date.today()
        pDD.daySpent=int(d)
        pDD.medicineCost=int(request.POST['medicineCost'])
        pDD.roomCharge=int(request.POST['roomCharge'])*int(d)
        pDD.doctorFee=int(request.POST['doctorFee'])
        pDD.OtherCharge=int(request.POST['OtherCharge'])
        pDD.total=(int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
        pDD.save()
        return render(request,'hospital/patient_final_bill.html',context=patientDict)
    return render(request,'hospital/patient_generate_bill.html',context=patientDict)



#--------------for discharge patient bill (pdf) download and printing
import io
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    from xhtml2pdf import pisa
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return



def download_pdf_view(request,pk):
    dischargeDetails=models.PatientDischargeDetails.objects.all().filter(patientId=pk).order_by('-id')[:1]
    dict={
        'patientName':dischargeDetails[0].patientName,
        'assignedDoctorName':dischargeDetails[0].assignedDoctorName,
        'address':dischargeDetails[0].address,
        'mobile':dischargeDetails[0].mobile,
        'symptoms':dischargeDetails[0].symptoms,
        'admitDate':dischargeDetails[0].admitDate,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'medicineCost':dischargeDetails[0].medicineCost,
        'roomCharge':dischargeDetails[0].roomCharge,
        'doctorFee':dischargeDetails[0].doctorFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
    }
    return render_to_pdf('hospital/download_bill.html',dict)



#-----------------APPOINTMENT START--------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_appointment_view(request):
    return render(request,'hospital/admin_appointment.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_view_appointment_view(request):
    appointments=models.Appointment.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_appointment.html',{'appointments':appointments})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_add_appointment_view(request):
    appointmentForm=forms.AppointmentForm()
    mydict={'appointmentForm':appointmentForm,}
    if request.method=='POST':
        appointmentForm=forms.AppointmentForm(request.POST)
        if appointmentForm.is_valid():
            appointment=appointmentForm.save(commit=False)
            appointment.doctorId=request.POST.get('doctorId')
            appointment.patientId=request.POST.get('patientId')
            appointment.doctorName=models.User.objects.get(id=request.POST.get('doctorId')).first_name
            appointment.patientName=models.User.objects.get(id=request.POST.get('patientId')).first_name
            appointment.status=True
            appointment.save()
        return HttpResponseRedirect('admin-view-appointment')
    return render(request,'hospital/admin_add_appointment.html',context=mydict)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_approve_appointment_view(request):
    #those whose approval are needed
    appointments=models.Appointment.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_appointment.html',{'appointments':appointments})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def approve_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.status=True
    appointment.save()
    return redirect(reverse('admin-approve-appointment'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def reject_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    return redirect('admin-approve-appointment')
#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------






#---------------------------------------------------------------------------------
#------------------------ DOCTOR RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor, login_url="doctorlogin")
def doctor_dashboard_view(request):
    #for three cards
    patientcount=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id).count()
    appointmentcount=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id).count()
    patientdischarged=models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.first_name).count()

    #for  table in doctor dashboard
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id).order_by('-id')
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid).order_by('-id')
    appointments=zip(appointments,patients)
    mydict={
    'patientcount':patientcount,
    'appointmentcount':appointmentcount,
    'patientdischarged':patientdischarged,
    'appointments':appointments,
    'doctor':models.Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
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
    dischargedpatients=models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.first_name)
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
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
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_view_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor, login_url="doctorlogin")
def doctor_delete_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor, login_url="doctorlogin")
def delete_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})



#---------------------------------------------------------------------------------
#------------------------ DOCTOR RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------






#---------------------------------------------------------------------------------
#------------------------ PATIENT RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='patientlogin')
@user_passes_test(is_patient, login_url="patientlogin")
def patient_dashboard_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id)
    doctor=models.Doctor.objects.get(user_id=patient.assignedDoctorId)
    mydict={
    'patient':patient,
    'doctorName':doctor.get_name,
    'doctorMobile':doctor.mobile,
    'doctorAddress':doctor.address,
    'symptoms':patient.symptoms,
    'doctorDepartment':doctor.department,
    'admitDate':patient.admitDate,
    }
    return render(request,'hospital/patient_dashboard.html',context=mydict)



@login_required(login_url='patientlogin')
@user_passes_test(is_patient, login_url="patientlogin")
def patient_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'hospital/patient_appointment.html',{'patient':patient})



@login_required(login_url='patientlogin')
@user_passes_test(is_patient, login_url="patientlogin")
def patient_book_appointment_view(request):
    appointmentForm=forms.PatientAppointmentForm()
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    message=None
    mydict={'appointmentForm':appointmentForm,'patient':patient,'message':message}
    if request.method=='POST':
        appointmentForm=forms.PatientAppointmentForm(request.POST)
        if appointmentForm.is_valid():
            print(request.POST.get('doctorId'))
            desc=request.POST.get('description')

            doctor=models.Doctor.objects.get(user_id=request.POST.get('doctorId'))
            
            appointment=appointmentForm.save(commit=False)
            appointment.doctorId=request.POST.get('doctorId')
            appointment.patientId=request.user.id #----user can choose any patient but only their info will be stored
            appointment.doctorName=models.User.objects.get(id=request.POST.get('doctorId')).first_name
            appointment.patientName=request.user.first_name #----user can choose any patient but only their info will be stored
            appointment.status=False
            appointment.save()
        return HttpResponseRedirect('patient-view-appointment')
    return render(request,'hospital/patient_book_appointment.html',context=mydict)



def patient_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'hospital/patient_view_doctor.html',{'patient':patient,'doctors':doctors})



def search_doctor_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    
    # whatever user write in search box we get in query
    query = request.GET['query']
    doctors=models.Doctor.objects.all().filter(status=True).filter(Q(department__icontains=query)| Q(user__first_name__icontains=query))
    return render(request,'hospital/patient_view_doctor.html',{'patient':patient,'doctors':doctors})




@login_required(login_url='patientlogin')
@user_passes_test(is_patient, login_url="patientlogin")
def patient_view_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    appointments=models.Appointment.objects.all().filter(patientId=request.user.id)
    return render(request,'hospital/patient_view_appointment.html',{'appointments':appointments,'patient':patient})



@login_required(login_url='patientlogin')
@user_passes_test(is_patient, login_url="patientlogin")
def patient_discharge_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    dischargeDetails=models.PatientDischargeDetails.objects.all().filter(patientId=patient.id).order_by('-id')[:1]
    patientDict=None
    if dischargeDetails:
        patientDict ={
        'is_discharged':True,
        'patient':patient,
        'patientId':patient.id,
        'patientName':patient.get_name,
        'assignedDoctorName':dischargeDetails[0].assignedDoctorName,
        'address':patient.address,
        'mobile':patient.mobile,
        'symptoms':patient.symptoms,
        'admitDate':patient.admitDate,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'medicineCost':dischargeDetails[0].medicineCost,
        'roomCharge':dischargeDetails[0].roomCharge,
        'doctorFee':dischargeDetails[0].doctorFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
        }
        print(patientDict)
    else:
        patientDict={
            'is_discharged':False,
            'patient':patient,
            'patientId':request.user.id,
        }
    return render(request,'hospital/patient_discharge.html',context=patientDict)


#------------------------ PATIENT RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------








#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START ------------------------------
#---------------------------------------------------------------------------------
def aboutus_view(request):
    return render(request,'hospital/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message,settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'hospital/contactussuccess.html')
    return render(request, 'hospital/contactus.html', {'form':sub})


#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------


# =========================================================================
# ======================== 义诊活动 ACTIVITY VIEWS =========================
# =========================================================================

@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_activity_view(request):
    activities = models.Activity.objects.all().order_by('-created_at')
    return render(request, 'hospital/admin_activity.html', {'activities': activities})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_add_activity_view(request):
    form = forms.ActivityForm()
    if request.method == 'POST':
        form = forms.ActivityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin-activity')
    return render(request, 'hospital/admin_add_activity.html', {'form': form})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_view_activity_view(request, pk):
    activity = models.Activity.objects.get(id=pk)
    participants = models.ActivityParticipant.objects.filter(activity=activity).select_related('user')
    return render(request, 'hospital/admin_view_activity.html', {
        'activity': activity, 'participants': participants
    })


@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def update_activity_view(request, pk):
    activity = models.Activity.objects.get(id=pk)
    form = forms.ActivityForm(instance=activity)
    if request.method == 'POST':
        form = forms.ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            return redirect('admin-activity')
    return render(request, 'hospital/admin_update_activity.html', {'form': form, 'activity': activity})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def delete_activity_view(request, pk):
    models.Activity.objects.get(id=pk).delete()
    return redirect('admin-activity')


# =========================================================================
# ======================== 志愿者 VOLUNTEER VIEWS ==========================
# =========================================================================

@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_volunteer_view(request):
    volunteers = models.Volunteer.objects.filter(status=True).select_related('user')
    pending = models.Volunteer.objects.filter(status=False).select_related('user')
    return render(request, 'hospital/admin_volunteer.html', {
        'volunteers': volunteers, 'pending': pending
    })


@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_add_volunteer_view(request):
    userForm = forms.VolunteerUserForm()
    volunteerForm = forms.VolunteerForm()
    if request.method == 'POST':
        userForm = forms.VolunteerUserForm(request.POST)
        volunteerForm = forms.VolunteerForm(request.POST)
        if userForm.is_valid() and volunteerForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            v = volunteerForm.save(commit=False)
            v.user = user
            v.status = True
            v.save()
            Group.objects.get_or_create(name='VOLUNTEER')[0].user_set.add(user)
            return redirect('admin-volunteer')
    return render(request, 'hospital/admin_add_volunteer.html', {
        'userForm': userForm, 'volunteerForm': volunteerForm
    })


@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def approve_volunteer_view(request, pk):
    models.Volunteer.objects.filter(id=pk).update(status=True)
    return redirect('admin-volunteer')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def reject_volunteer_view(request, pk):
    v = models.Volunteer.objects.get(id=pk)
    v.user.delete()  # 级联删除 Volunteer
    return redirect('admin-volunteer')


# =========================================================================
# ============================ 站点 STATION VIEWS =========================
# =========================================================================

@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_station_view(request):
    stations = models.Station.objects.all().order_by('-id')
    return render(request, 'hospital/admin_station.html', {'stations': stations})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_add_station_view(request):
    form = forms.StationForm()
    if request.method == 'POST':
        form = forms.StationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin-station')
    return render(request, 'hospital/admin_add_station.html', {'form': form})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def update_station_view(request, pk):
    station = models.Station.objects.get(id=pk)
    form = forms.StationForm(instance=station)
    if request.method == 'POST':
        form = forms.StationForm(request.POST, instance=station)
        if form.is_valid():
            form.save()
            return redirect('admin-station')
    return render(request, 'hospital/admin_update_station.html', {'form': form, 'station': station})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def delete_station_view(request, pk):
    models.Station.objects.get(id=pk).delete()
    return redirect('admin-station')


# =========================================================================
# ===================== 病历 MEDICAL RECORD VIEWS (Admin) =================
# =========================================================================

@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_medical_records_view(request):
    records = models.MedicalRecord.objects.all().order_by('-created_at').select_related('patient', 'doctor')
    return render(request, 'hospital/admin_medical_records.html', {'records': records})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def admin_view_record_view(request, pk):
    record = models.MedicalRecord.objects.get(id=pk)
    findings = models.ToothFinding.objects.filter(record=record)
    history = getattr(record.patient, 'medical_history', None)
    return render(request, 'hospital/admin_view_record.html', {
        'record': record, 'findings': findings, 'history': history
    })


# =========================================================================
# ===================== 病历 MEDICAL RECORD VIEWS (Doctor) ================
# =========================================================================

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor, login_url="doctorlogin")
def doctor_records_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    records = models.MedicalRecord.objects.filter(doctor=request.user).order_by('-created_at').select_related('patient')
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
            record.doctor = request.user
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

@login_required(login_url='patientlogin')
@user_passes_test(is_patient, login_url="patientlogin")
def patient_records_view(request):
    """患者查看自己的病历列表"""
    patient = models.Patient.objects.get(user=request.user)
    records = models.MedicalRecord.objects.filter(patient=patient).order_by('-check_date', '-created_at')
    return render(request, 'hospital/patient_records.html', {
        'patient': patient, 'records': records
    })


@login_required(login_url='patientlogin')
@user_passes_test(is_patient, login_url="patientlogin")
def patient_view_record_view(request, pk):
    """患者查看单个病历详情"""
    patient = models.Patient.objects.get(user=request.user)
    record = models.MedicalRecord.objects.get(id=pk, patient=patient)
    findings = models.ToothFinding.objects.filter(record=record)

    # 获取医生名称
    doctor_name = None
    if record.doctor:
        try:
            doctor = models.Doctor.objects.get(user=record.doctor)
            doctor_name = doctor.get_name
        except models.Doctor.DoesNotExist:
            doctor_name = record.doctor.get_full_name() or record.doctor.username

    # 构建牙位查找字典，键为牙位号，值为finding对象
    findings_dict = {}
    for finding in findings:
        findings_dict[finding.tooth_number] = finding

    return render(request, 'hospital/patient_view_record.html', {
        'patient': patient,
        'record': record,
        'findings': findings,
        'doctor_name': doctor_name,
        'findings_dict': findings_dict,
        # FDI 牙位编号
        'upper_right': [11, 12, 13, 14, 15, 16, 17, 18],
        'upper_left': [21, 22, 23, 24, 25, 26, 27, 28],
        'lower_left': [31, 32, 33, 34, 35, 36, 37, 38],
        'lower_right': [41, 42, 43, 44, 45, 46, 47, 48],
    })
