from hospital import models
from hospital.tests.e2e.base import WebUITestCase
from hospital.tests.helpers import (
    DEFAULT_PASSWORD,
    create_appointment,
    create_doctor,
    create_patient,
    create_record,
)


class DoctorWebUITests(WebUITestCase):
    def test_doctor_appointment_list_shows_duplicate_patient_appointments(self):
        doctor_user, doctor = create_doctor(username="e2e_duplicate_doctor")
        _, patient = create_patient(username="e2e_duplicate_patient", assigned_doctor=doctor)
        for description in ("E2E first follow up", "E2E second follow up"):
            models.Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                patientName=patient.get_name,
                doctorName=doctor.get_name,
                description=description,
                status=True,
            )

        self.login("/doctorlogin", doctor_user.username, DEFAULT_PASSWORD)
        self.goto("/doctor-view-appointment")

        self.assert_page_contains("E2E first follow up")
        self.assert_page_contains("E2E second follow up")

    def test_doctor_appointment_list_renders_default_avatar_for_patient_without_picture(self):
        doctor_user, doctor = create_doctor(username="e2e_avatar_doctor")
        _, patient = create_patient(username="e2e_avatar_patient", assigned_doctor=doctor)
        models.Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            patientName=patient.get_name,
            doctorName=doctor.get_name,
            description="E2E avatar appointment",
            status=True,
        )

        self.login("/doctorlogin", doctor_user.username, DEFAULT_PASSWORD)
        self.goto("/doctor-view-appointment")

        self.assert_page_contains("E2E avatar appointment")
        self.assert_page_contains("Default Profile Pic")

    def test_doctor_delete_page_only_shows_current_doctor_appointments(self):
        doctor_user, doctor = create_doctor(username="e2e_visible_doctor")
        _, other_doctor = create_doctor(username="e2e_hidden_doctor")
        _, visible_patient = create_patient(username="e2e_visible_patient", assigned_doctor=doctor)
        _, hidden_patient = create_patient(username="e2e_hidden_patient", assigned_doctor=other_doctor)
        models.Appointment.objects.create(
            patient=visible_patient,
            doctor=doctor,
            patientName=visible_patient.get_name,
            doctorName=doctor.get_name,
            description="E2E visible appointment",
            status=True,
        )
        models.Appointment.objects.create(
            patient=hidden_patient,
            doctor=other_doctor,
            patientName=hidden_patient.get_name,
            doctorName=other_doctor.get_name,
            description="E2E hidden appointment",
            status=True,
        )

        self.login("/doctorlogin", doctor_user.username, DEFAULT_PASSWORD)
        self.goto("/doctor-delete-appointment")

        self.assert_page_contains("E2E visible appointment")
        self.assertNotIn("E2E hidden appointment", self.page.content())
        self.assertGreater(
            self.page.locator('form[action*="/delete-appointment/"] button[type="submit"]').count(),
            0,
        )

    def test_doctor_dashboard_and_patient_list_load(self):
        doctor_user, doctor = create_doctor(username="e2e_doctor_dashboard")
        _, patient = create_patient(
            username="e2e_doctor_dashboard_patient",
            assigned_doctor=doctor,
            symptoms="E2E dashboard symptom",
        )

        self.login("/doctorlogin", doctor_user.username, DEFAULT_PASSWORD)
        self.goto("/doctor-dashboard")
        self.assert_page_contains("Patient Under You")
        self.goto("/doctor-view-patient")
        self.assert_page_contains(patient.get_name)
        self.assert_page_contains("E2E dashboard symptom")

    def test_doctor_patient_search_filters_assigned_patients(self):
        doctor_user, doctor = create_doctor(username="e2e_doctor_search")
        _, other_doctor = create_doctor(username="e2e_other_search_doctor")
        _, matching = create_patient(
            username="e2e_matching_patient",
            assigned_doctor=doctor,
            symptoms="RareSearchSymptom",
        )
        _, hidden = create_patient(
            username="e2e_hidden_search_patient",
            assigned_doctor=doctor,
            symptoms="Common symptom",
        )
        _, other_doctor_patient = create_patient(
            username="e2e_other_search_patient",
            assigned_doctor=other_doctor,
            symptoms="RareSearchSymptom",
        )

        self.login("/doctorlogin", doctor_user.username, DEFAULT_PASSWORD)
        self.goto("/search?query=RareSearchSymptom")

        self.assert_page_contains(matching.get_name)
        self.assertNotIn(hidden.get_name, self.page.content())
        self.assertNotIn(other_doctor_patient.get_name, self.page.content())

    def test_doctor_can_delete_own_appointment_from_ui(self):
        doctor_user, doctor = create_doctor(username="e2e_delete_own_doctor")
        _, patient = create_patient(
            username="e2e_delete_own_patient",
            assigned_doctor=doctor,
        )
        appointment = create_appointment(
            patient=patient,
            doctor=doctor,
            description="E2E delete own appointment",
            status=True,
        )

        self.login("/doctorlogin", doctor_user.username, DEFAULT_PASSWORD)
        self.goto("/doctor-delete-appointment")
        self.assert_page_contains("E2E delete own appointment")
        self.click_form_action(f"/delete-appointment/{appointment.id}")

        self.assert_url_contains("/doctor-delete-appointment")
        self.assertFalse(models.Appointment.objects.filter(id=appointment.id).exists())

    def test_doctor_can_create_and_confirm_medical_record(self):
        doctor_user, doctor = create_doctor(username="e2e_record_doctor")
        _, patient = create_patient(
            username="e2e_record_patient",
            assigned_doctor=doctor,
        )
        _, other_doctor = create_doctor(username="e2e_record_other_doctor")
        _, other_patient = create_patient(
            username="e2e_record_other_patient",
            assigned_doctor=other_doctor,
        )
        other_record = create_record(
            patient=other_patient,
            doctor=other_doctor,
            chief_complaint="E2E other doctor hidden complaint",
            diagnosis="E2E other doctor hidden diagnosis",
        )

        self.login("/doctorlogin", doctor_user.username, DEFAULT_PASSWORD)
        self.goto("/doctor-create-record")
        self.page.locator('select[name="patient"]').select_option(str(patient.id))
        self.page.locator('input[name="check_date"]').fill("2026-06-22")
        self.page.locator('textarea[name="chief_complaint"]').fill("E2E tooth pain")
        self.page.locator('textarea[name="diagnosis"]').fill("E2E caries diagnosis")
        self.submit_first_form()

        self.assert_url_contains("/doctor-records")
        record = models.MedicalRecord.objects.get(patient=patient, doctor=doctor)
        self.assertEqual(record.chief_complaint, "E2E tooth pain")
        self.assertFalse(record.doctor_confirmed)
        self.assert_page_contains(record.visit_no)
        self.assert_page_contains("E2E tooth pain")

        self.page.locator(f'a[href="/doctor-update-record/{record.id}"]').click()
        self.page.wait_for_load_state("networkidle")
        self.page.locator('input[name="doctor_confirmed"]').check()
        self.submit_first_form()

        record.refresh_from_db()
        self.assertTrue(record.doctor_confirmed)
        self.assertIsNotNone(record.confirmed_at)

        response = self.page.request.get(
            f"{self.live_server_url}/doctor-update-record/{other_record.id}"
        )
        self.assertEqual(response.status, 404)
        self.assertNotIn("E2E other doctor hidden complaint", response.text())

        other_record.refresh_from_db()
        self.assertEqual(other_record.doctor, other_doctor)
        self.assertFalse(other_record.doctor_confirmed)
        self.assertEqual(
            other_record.chief_complaint,
            "E2E other doctor hidden complaint",
        )
