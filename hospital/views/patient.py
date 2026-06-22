from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from hospital import forms, models
from .common import is_patient


@login_required(login_url='patientlogin')
@user_passes_test(is_patient, login_url="patientlogin")
def patient_dashboard_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id)
    doctor=models.Doctor.objects.filter(user_id=patient.assignedDoctorId).first()
    mydict={
    'patient':patient,
    'doctorName':doctor.get_name if doctor else '未分配',
    'doctorMobile':doctor.mobile if doctor else '',
    'doctorAddress':doctor.address if doctor else '',
    'symptoms':patient.symptoms,
    'doctorDepartment':doctor.department if doctor else '',
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
        mydict={'appointmentForm':appointmentForm,'patient':patient,'message':message}
        if appointmentForm.is_valid():
            appointment=appointmentForm.save(commit=False)
            appointment.patient=models.Patient.objects.get(user=request.user)
            appointment.doctorName=appointment.doctor.get_name
            appointment.patientName=request.user.first_name
            appointment.status=False
            appointment.save()
            return HttpResponseRedirect('patient-view-appointment')
    return render(request,'hospital/patient_book_appointment.html',context=mydict)

@login_required(login_url='patientlogin')
@user_passes_test(is_patient, login_url="patientlogin")
def patient_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    patient=models.Patient.objects.get(user_id=request.user.id)
    return render(request,'hospital/patient_view_doctor.html',{'patient':patient,'doctors':doctors})

@login_required(login_url='patientlogin')
@user_passes_test(is_patient, login_url="patientlogin")
def search_doctor_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id)
    query = request.GET.get('query', '').strip()
    if not query:
        return render(request,'hospital/patient_view_doctor.html',{'patient':patient,'doctors':[]})
    doctors=models.Doctor.objects.filter(status=True).filter(Q(department__icontains=query)| Q(user__first_name__icontains=query))
    return render(request,'hospital/patient_view_doctor.html',{'patient':patient,'doctors':doctors})

@login_required(login_url='patientlogin')
@user_passes_test(is_patient, login_url="patientlogin")
def patient_view_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    appointments=models.Appointment.objects.filter(patient__user=request.user)
    return render(request,'hospital/patient_view_appointment.html',{'appointments':appointments,'patient':patient})

@login_required(login_url='patientlogin')
@user_passes_test(is_patient, login_url="patientlogin")
def patient_discharge_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    dischargeDetails=models.PatientDischargeDetails.objects.filter(patient=patient).order_by('-id')[:1]
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
    record = get_object_or_404(models.MedicalRecord, id=pk, patient=patient)
    findings = models.ToothFinding.objects.filter(record=record)

    # record.doctor 已是 FK(Doctor)，直接取名
    doctor_name = record.doctor.get_name if record.doctor else None

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
