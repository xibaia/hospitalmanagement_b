import io
from datetime import date

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, reverse
from django.template.loader import get_template

from hospital import forms, models
from .common import is_admin


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
    if request.method != 'POST':
        return redirect('admin-view-doctor')
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

    userForm=forms.DoctorUserUpdateForm(instance=user)
    doctorForm=forms.DoctorForm(request.FILES,instance=doctor)
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserUpdateForm(request.POST,instance=user)
        doctorForm=forms.DoctorForm(request.POST,request.FILES,instance=doctor)
        if userForm.is_valid() and doctorForm.is_valid():
            userForm.save()                    # 不含 password，不会覆盖密码
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
    if request.method != 'POST':
        return redirect(reverse('admin-approve-doctor'))
    doctor=models.Doctor.objects.get(id=pk)
    doctor.status=True
    doctor.save()
    return redirect(reverse('admin-approve-doctor'))

@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def reject_doctor_view(request,pk):
    if request.method != 'POST':
        return redirect('admin-approve-doctor')
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
    if request.method != 'POST':
        return redirect('admin-view-patient')
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

    userForm=forms.PatientUserUpdateForm(instance=user)
    patientForm=forms.PatientForm(request.FILES,instance=patient)
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserUpdateForm(request.POST,instance=user)
        patientForm=forms.PatientForm(request.POST,request.FILES,instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            userForm.save()                    # 不含 password，不会覆盖密码
            patient=patientForm.save(commit=False)
            patient.status=True
            doc_id = request.POST.get('assignedDoctorId')
            if doc_id and models.Doctor.objects.filter(user_id=doc_id, status=True).exists():
                patient.assignedDoctorId=doc_id
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
    if request.method != 'POST':
        return redirect(reverse('admin-approve-patient'))
    patient=models.Patient.objects.get(id=pk)
    patient.status=True
    patient.save()
    return redirect(reverse('admin-approve-patient'))

@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def reject_patient_view(request,pk):
    if request.method != 'POST':
        return redirect('admin-approve-patient')
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
    days=(date.today()-patient.admitDate)
    d=days.days
    # 兼容 assignedDoctorId 为空或无效的情况
    assignedDoctor=models.Doctor.objects.filter(user_id=patient.assignedDoctorId).first()
    assignedDoctorName = assignedDoctor.get_name if assignedDoctor else '未指定'
    patientDict={
        'patientId':pk,
        'name':patient.get_name,
        'mobile':patient.mobile,
        'address':patient.address,
        'symptoms':patient.symptoms,
        'admitDate':patient.admitDate,
        'todayDate':date.today(),
        'day':d,
        'assignedDoctorName':assignedDoctorName,
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
        pDD.patient=patient
        pDD.patientName=patient.get_name
        pDD.assignedDoctorName=assignedDoctorName
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
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result, encoding='UTF-8')
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return

@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def download_pdf_view(request,pk):
    dischargeDetails=models.PatientDischargeDetails.objects.filter(patient_id=pk).order_by('-id')[:1]
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
            appointment.doctorName=appointment.doctor.get_name
            appointment.patientName=appointment.patient.get_name
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
    if request.method != 'POST':
        return redirect(reverse('admin-approve-appointment'))
    appointment=models.Appointment.objects.get(id=pk)
    appointment.status=True
    appointment.save()
    return redirect(reverse('admin-approve-appointment'))

@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def reject_appointment_view(request,pk):
    if request.method != 'POST':
        return redirect('admin-approve-appointment')
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    return redirect('admin-approve-appointment')
#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------






#---------------------------------------------------------------------------------
#------------------------ DOCTOR RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------

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
    if request.method != 'POST':
        return redirect('admin-activity')
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
    if request.method != 'POST':
        return redirect('admin-volunteer')
    models.Volunteer.objects.filter(id=pk).update(status=True)
    return redirect('admin-volunteer')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url="adminlogin")
def reject_volunteer_view(request, pk):
    if request.method != 'POST':
        return redirect('admin-volunteer')
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
    if request.method != 'POST':
        return redirect('admin-station')
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
