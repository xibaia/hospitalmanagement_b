from hospital import models
from hospital.tests.e2e.base import WebUITestCase
from hospital.tests.helpers import (
    DEFAULT_PASSWORD,
    create_discharge,
    create_doctor,
    create_grouped_user,
    create_patient,
    create_record,
)


class PatientWebUITests(WebUITestCase):
    def test_patient_book_appointment_empty_form_stays_on_page(self):
        patient_user, _ = create_patient(username="e2e_empty_booking_patient")

        self.login("/patientlogin", patient_user.username, DEFAULT_PASSWORD)
        self.goto("/patient-book-appointment")
        self.page.locator('button[type="submit"]').click()
        self.page.wait_for_load_state("networkidle")

        self.assertIn("/patient-book-appointment", self.page.url)
        self.assertEqual(models.Appointment.objects.count(), 0)

    def test_patient_can_request_appointment_and_see_pending_record(self):
        _, doctor = create_doctor(username="e2e_patient_booking_doctor")
        patient_user, patient = create_patient(
            username="e2e_booking_patient",
            assigned_doctor=doctor,
        )

        self.login("/patientlogin", patient_user.username, DEFAULT_PASSWORD)
        self.goto("/patient-book-appointment")
        self.page.locator('select[name="doctor"]').select_option(str(doctor.id))
        self.page.locator('textarea[name="description"]').fill(
            "E2E patient booking request"
        )
        self.submit_first_form()

        self.assert_url_contains("/patient-view-appointment")
        appointment = models.Appointment.objects.get(
            description="E2E patient booking request"
        )
        self.assertEqual(appointment.patient, patient)
        self.assertEqual(appointment.doctor, doctor)
        self.assertFalse(appointment.status)
        self.assert_page_contains("E2E patient booking request")

    def test_patient_booking_becomes_visible_to_doctor_after_admin_approval(self):
        admin = create_grouped_user("e2e_patient_flow_admin", "ADMIN")
        doctor_user, doctor = create_doctor(username="e2e_patient_flow_doctor")
        patient_user, _ = create_patient(
            username="e2e_patient_flow_patient",
            assigned_doctor=doctor,
        )

        self.login("/patientlogin", patient_user.username, DEFAULT_PASSWORD)
        self.goto("/patient-book-appointment")
        self.page.locator('select[name="doctor"]').select_option(str(doctor.id))
        self.page.locator('textarea[name="description"]').fill(
            "E2E cross-role appointment"
        )
        self.submit_first_form()
        appointment = models.Appointment.objects.get(
            description="E2E cross-role appointment"
        )
        self.logout()

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-approve-appointment")
        self.click_form_action(f"/approve-appointment/{appointment.id}")
        appointment.refresh_from_db()
        self.assertTrue(appointment.status)
        self.logout()

        self.login("/doctorlogin", doctor_user.username, DEFAULT_PASSWORD)
        self.goto("/doctor-view-appointment")
        self.assert_page_contains("E2E cross-role appointment")

    def test_patient_can_view_and_search_approved_doctors(self):
        patient_user, _ = create_patient(username="e2e_doctor_list_patient")
        _, approved_doctor = create_doctor(
            username="e2e_visible_list_doctor",
            department="E2E Visible Dentistry",
            status=True,
        )
        _, pending_doctor = create_doctor(
            username="e2e_hidden_list_doctor",
            department="E2E Hidden Dentistry",
            status=False,
        )

        self.login("/patientlogin", patient_user.username, DEFAULT_PASSWORD)
        self.goto("/patient-view-doctor")

        self.assert_page_contains(approved_doctor.get_name)
        self.assert_page_contains("E2E Visible Dentistry")
        self.assertNotIn(pending_doctor.get_name, self.page.content())
        self.assertNotIn("E2E Hidden Dentistry", self.page.content())

        self.goto("/searchdoctor?query=Visible%20Dentistry")

        self.assert_page_contains(approved_doctor.get_name)
        self.assertNotIn(pending_doctor.get_name, self.page.content())

    def test_patient_can_view_own_medical_record_detail(self):
        _, doctor = create_doctor(username="e2e_patient_record_doctor")
        patient_user, patient = create_patient(
            username="e2e_patient_record_patient",
            assigned_doctor=doctor,
        )
        _, other_doctor = create_doctor(username="e2e_other_patient_record_doctor")
        _, other_patient = create_patient(
            username="e2e_other_patient_record_patient",
            assigned_doctor=other_doctor,
        )
        record = create_record(
            patient=patient,
            doctor=doctor,
            chief_complaint="E2E patient visible complaint",
            diagnosis="E2E patient visible diagnosis",
        )
        other_record = create_record(
            patient=other_patient,
            doctor=other_doctor,
            chief_complaint="E2E other patient hidden complaint",
            diagnosis="E2E other patient hidden diagnosis",
        )

        self.login("/patientlogin", patient_user.username, DEFAULT_PASSWORD)
        self.goto("/patient-records")
        self.assert_page_contains(record.visit_no)
        self.assertNotIn(other_record.visit_no, self.page.content())
        self.assertNotIn("E2E other patient hidden complaint", self.page.content())

        response = self.page.request.get(
            f"{self.live_server_url}/patient-view-record/{other_record.id}"
        )
        self.assertEqual(response.status, 404)
        self.assertNotIn("E2E other patient hidden complaint", response.text())

        self.goto(f"/patient-view-record/{record.id}")

        self.assert_page_contains("E2E patient visible complaint")
        self.assert_page_contains("E2E patient visible diagnosis")

    def test_patient_can_view_latest_discharge_bill(self):
        _, doctor = create_doctor(username="e2e_patient_discharge_doctor")
        patient_user, patient = create_patient(
            username="e2e_patient_discharge_patient",
            assigned_doctor=doctor,
        )
        create_discharge(
            patient=patient,
            assigned_doctor_name=doctor.get_name,
            total=460,
        )

        self.login("/patientlogin", patient_user.username, DEFAULT_PASSWORD)
        self.goto("/patient-discharge")

        self.assert_page_contains(patient.get_name)
        self.assert_page_contains(doctor.get_name)
        self.assert_page_contains("460")
