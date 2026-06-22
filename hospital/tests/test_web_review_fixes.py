from django.test import TestCase
from django.urls import reverse

from hospital import models
from hospital.forms import MedicalRecordForm
from hospital.tests.helpers import (
    create_activity,
    create_doctor,
    create_grouped_user,
    create_patient,
    create_record,
)


class WebApprovalPermissionTests(TestCase):
    def test_pending_doctor_cannot_open_doctor_dashboard_directly(self):
        pending_doctor_user, _ = create_doctor(
            username="pending_web_doctor",
            status=False,
        )
        self.client.force_login(pending_doctor_user)

        direct_response = self.client.get(reverse("doctor-dashboard"))
        afterlogin_response = self.client.get(reverse("afterlogin"))

        self.assertEqual(direct_response.status_code, 302)
        self.assertTemplateUsed(afterlogin_response, "hospital/doctor_wait_for_approval.html")

    def test_pending_patient_cannot_open_patient_dashboard_directly(self):
        pending_patient_user, _ = create_patient(
            username="pending_web_patient",
            status=False,
        )
        self.client.force_login(pending_patient_user)

        direct_response = self.client.get(reverse("patient-dashboard"))
        afterlogin_response = self.client.get(reverse("afterlogin"))

        self.assertEqual(direct_response.status_code, 302)
        self.assertTemplateUsed(afterlogin_response, "hospital/patient_wait_for_approval.html")


class AdminPostActionTemplateTests(TestCase):
    def test_approve_doctor_requires_post_and_template_uses_post_form(self):
        admin_user = create_grouped_user("review_admin", "ADMIN")
        _, pending_doctor = create_doctor(
            username="post_approval_doctor",
            status=False,
        )
        self.client.force_login(admin_user)

        page_response = self.client.get(reverse("admin-approve-doctor"))
        self.assertContains(
            page_response,
            f'method="post" action="{reverse("approve-doctor", args=[pending_doctor.id])}"',
        )

        get_response = self.client.get(reverse("approve-doctor", args=[pending_doctor.id]))
        pending_doctor.refresh_from_db()
        self.assertEqual(get_response.status_code, 302)
        self.assertFalse(pending_doctor.status)

        post_response = self.client.post(reverse("approve-doctor", args=[pending_doctor.id]))
        pending_doctor.refresh_from_db()
        self.assertEqual(post_response.status_code, 302)
        self.assertTrue(pending_doctor.status)


class WebTemplateRobustnessTests(TestCase):
    def test_admin_activity_allows_activity_without_leader(self):
        admin_user = create_grouped_user("activity_admin", "ADMIN")
        create_activity(name="No leader activity", leader=None)
        self.client.force_login(admin_user)

        response = self.client.get(reverse("admin-activity"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "未指定")

    def test_admin_medical_records_renders_doctor_model_name(self):
        admin_user = create_grouped_user("records_admin", "ADMIN")
        _, doctor = create_doctor(username="records_doctor", real_name="Record Doctor")
        _, patient = create_patient(username="records_patient", assigned_doctor=doctor)
        create_record(patient=patient, doctor=doctor)
        self.client.force_login(admin_user)

        response = self.client.get(reverse("admin-medical-records"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Record Doctor")

    def test_doctor_appointment_lists_allow_patient_without_profile_pic(self):
        doctor_user, doctor = create_doctor(username="appointment_doctor")
        _, patient = create_patient(username="appointment_patient", assigned_doctor=doctor)
        models.Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            patientName=patient.get_name,
            doctorName=doctor.get_name,
            description="Follow up",
            status=True,
        )
        self.client.force_login(doctor_user)

        view_response = self.client.get(reverse("doctor-view-appointment"))
        delete_response = self.client.get(reverse("doctor-delete-appointment"))

        self.assertEqual(view_response.status_code, 200)
        self.assertEqual(delete_response.status_code, 200)
        self.assertContains(view_response, "Default Profile Pic")
        self.assertContains(delete_response, "Default Profile Pic")

    def test_doctor_appointment_lists_do_not_drop_duplicate_patient_appointments(self):
        doctor_user, doctor = create_doctor(username="duplicate_appt_doctor")
        _, patient = create_patient(username="duplicate_appt_patient", assigned_doctor=doctor)
        for description in ("First follow up", "Second follow up"):
            models.Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                patientName=patient.get_name,
                doctorName=doctor.get_name,
                description=description,
                status=True,
            )
        self.client.force_login(doctor_user)

        view_response = self.client.get(reverse("doctor-view-appointment"))
        delete_response = self.client.get(reverse("doctor-delete-appointment"))

        self.assertContains(view_response, "First follow up")
        self.assertContains(view_response, "Second follow up")
        self.assertContains(delete_response, "First follow up")
        self.assertContains(delete_response, "Second follow up")

    def test_doctor_delete_appointment_requires_post(self):
        doctor_user, doctor = create_doctor(username="delete_appt_doctor")
        _, patient = create_patient(username="delete_appt_patient", assigned_doctor=doctor)
        appointment = models.Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            patientName=patient.get_name,
            doctorName=doctor.get_name,
            description="Delete me",
            status=True,
        )
        self.client.force_login(doctor_user)

        get_response = self.client.get(reverse("delete-appointment", args=[appointment.id]))
        self.assertEqual(get_response.status_code, 302)
        self.assertTrue(models.Appointment.objects.filter(id=appointment.id).exists())

        post_response = self.client.post(reverse("delete-appointment", args=[appointment.id]))
        self.assertEqual(post_response.status_code, 302)
        self.assertFalse(models.Appointment.objects.filter(id=appointment.id).exists())

    def test_doctor_cannot_delete_another_doctors_appointment(self):
        doctor_user, _ = create_doctor(username="delete_appt_attacker")
        _, other_doctor = create_doctor(username="delete_appt_owner")
        _, patient = create_patient(username="other_doctor_patient", assigned_doctor=other_doctor)
        appointment = models.Appointment.objects.create(
            patient=patient,
            doctor=other_doctor,
            patientName=patient.get_name,
            doctorName=other_doctor.get_name,
            description="Protected appointment",
            status=True,
        )
        self.client.force_login(doctor_user)

        response = self.client.post(reverse("delete-appointment", args=[appointment.id]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(models.Appointment.objects.filter(id=appointment.id).exists())


class InvalidWebFormTests(TestCase):
    def test_patient_signup_mobile_pattern_accepts_chinese_mobile_numbers(self):
        response = self.client.get("/patientsignup")

        self.assertContains(response, 'pattern="1[3-9][0-9]{9}"')

    def test_admin_add_appointment_stays_on_form_when_invalid(self):
        admin_user = create_grouped_user("invalid_appt_admin", "ADMIN")
        self.client.force_login(admin_user)

        response = self.client.post(reverse("admin-add-appointment"), {})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hospital/admin_add_appointment.html")
        self.assertFalse(models.Appointment.objects.exists())

    def test_admin_add_doctor_stays_on_form_when_invalid(self):
        admin_user = create_grouped_user("invalid_doctor_admin", "ADMIN")
        self.client.force_login(admin_user)

        response = self.client.post(reverse("admin-add-doctor"), {})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hospital/admin_add_doctor.html")
        self.assertFalse(models.Doctor.objects.exists())

    def test_admin_add_patient_stays_on_form_when_invalid(self):
        admin_user = create_grouped_user("invalid_patient_admin", "ADMIN")
        self.client.force_login(admin_user)

        response = self.client.post(reverse("admin-add-patient"), {})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hospital/admin_add_patient.html")
        self.assertFalse(models.Patient.objects.exists())

    def test_patient_book_appointment_stays_on_form_when_invalid(self):
        patient_user, _ = create_patient(username="invalid_booking_patient")
        self.client.force_login(patient_user)

        response = self.client.post(reverse("patient-book-appointment"), {})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hospital/patient_book_appointment.html")
        self.assertFalse(models.Appointment.objects.exists())

    def test_public_doctor_signup_stays_on_form_when_invalid(self):
        response = self.client.post(reverse("doctorsignup"), {})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hospital/doctorsignup.html")
        self.assertFalse(models.Doctor.objects.exists())

    def test_public_patient_signup_stays_on_form_when_invalid(self):
        response = self.client.post("/patientsignup", {})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hospital/patientsignup.html")
        self.assertFalse(models.Patient.objects.exists())


class DoctorRecordConfirmationTests(TestCase):
    def test_medical_record_form_exposes_doctor_confirmed(self):
        self.assertIn("doctor_confirmed", MedicalRecordForm().fields)

    def test_doctor_update_record_can_confirm_record(self):
        doctor_user, doctor = create_doctor(username="confirming_web_doctor")
        _, patient = create_patient(
            username="confirming_record_patient",
            assigned_doctor=doctor,
        )
        record = create_record(patient=patient, doctor=doctor)
        self.client.force_login(doctor_user)

        response = self.client.post(
            reverse("doctor-update-record", args=[record.id]),
            {
                "patient": patient.id,
                "visit_type": record.visit_type,
                "check_date": record.check_date.isoformat(),
                "mouth_opening": record.mouth_opening,
                "diagnosis": "Confirmed diagnosis",
                "doctor_confirmed": "on",
                "tooth_findings-TOTAL_FORMS": "0",
                "tooth_findings-INITIAL_FORMS": "0",
                "tooth_findings-MIN_NUM_FORMS": "0",
                "tooth_findings-MAX_NUM_FORMS": "32",
            },
        )

        record.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(record.doctor_confirmed)
        self.assertIsNotNone(record.confirmed_at)
