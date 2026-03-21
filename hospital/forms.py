from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from . import models



#for admin signup
class AdminSigupForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }


#for student related form
class DoctorUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }
class DoctorForm(forms.ModelForm):
    class Meta:
        model=models.Doctor
        fields=['address','mobile','department','status','profile_pic']



#for teacher related form
class PatientUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }
class PatientForm(forms.ModelForm):
    #this is the extrafield for linking patient and their assigend doctor
    #this will show dropdown __str__ method doctor model is shown on html so override it
    #to_field_name this will fetch corresponding value  user_id present in Doctor model and return it
    assignedDoctorId=forms.ModelChoiceField(queryset=models.Doctor.objects.all().filter(status=True),empty_label="Name and Department", to_field_name="user_id")
    class Meta:
        model=models.Patient
        fields=['address','mobile','status','symptoms','profile_pic']



class AppointmentForm(forms.ModelForm):
    doctorId=forms.ModelChoiceField(queryset=models.Doctor.objects.all().filter(status=True),empty_label="Doctor Name and Department", to_field_name="user_id")
    patientId=forms.ModelChoiceField(queryset=models.Patient.objects.all().filter(status=True),empty_label="Patient Name and Symptoms", to_field_name="user_id")
    class Meta:
        model=models.Appointment
        fields=['description','status']


class PatientAppointmentForm(forms.ModelForm):
    doctorId=forms.ModelChoiceField(queryset=models.Doctor.objects.all().filter(status=True),empty_label="Doctor Name and Department", to_field_name="user_id")
    class Meta:
        model=models.Appointment
        fields=['description','status']


# ==================== 志愿者 ====================
class VolunteerUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {'password': forms.PasswordInput()}

class VolunteerForm(forms.ModelForm):
    class Meta:
        model = models.Volunteer
        fields = ['real_name', 'mobile']


# ==================== 义诊活动 ====================
class ActivityForm(forms.ModelForm):
    class Meta:
        model = models.Activity
        fields = ['name', 'location', 'start_time', 'end_time', 'description', 'leader', 'status']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


# ==================== 站点 ====================
class StationForm(forms.ModelForm):
    class Meta:
        model = models.Station
        fields = ['name', 'address', 'latitude', 'longitude', 'supervisor', 'phone', 'is_active']


# ==================== 病历 ====================
class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = models.MedicalRecord
        fields = [
            'patient', 'activity', 'visit_type', 'check_date',
            'chief_complaint', 'present_illness', 'past_history_note',
            'auxiliary_exam', 'treatment_plan', 'informed_consent',
            'treatment_record', 'followup_notes',
            'face_symmetry', 'has_swelling', 'mouth_opening',
            'extraoral_note', 'has_periodontal', 'mucosa_normal',
            'mucosa_note', 'intraoral_note', 'diagnosis',
        ]
        widgets = {
            'check_date': forms.DateInput(attrs={'type': 'date'}),
            'chief_complaint': forms.Textarea(attrs={'rows': 2}),
            'present_illness': forms.Textarea(attrs={'rows': 2}),
            'past_history_note': forms.Textarea(attrs={'rows': 2}),
            'auxiliary_exam': forms.Textarea(attrs={'rows': 2}),
            'treatment_plan': forms.Textarea(attrs={'rows': 3}),
            'informed_consent': forms.Textarea(attrs={'rows': 2}),
            'treatment_record': forms.Textarea(attrs={'rows': 3}),
            'followup_notes': forms.Textarea(attrs={'rows': 2}),
            'extraoral_note': forms.Textarea(attrs={'rows': 2}),
            'mucosa_note': forms.Textarea(attrs={'rows': 2}),
            'intraoral_note': forms.Textarea(attrs={'rows': 2}),
            'diagnosis': forms.Textarea(attrs={'rows': 2}),
        }


class ToothFindingForm(forms.ModelForm):
    class Meta:
        model = models.ToothFinding
        fields = ['tooth_number', 'finding_type', 'note']


# 牙位检查内联 formset，最多10条，可删除
ToothFindingFormSet = inlineformset_factory(
    models.MedicalRecord, models.ToothFinding,
    form=ToothFindingForm, extra=1, can_delete=True, max_num=32
)


#for contact us page
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))



#Developed By : sumit kumar
#facebook : fb.com/sumit.luv
