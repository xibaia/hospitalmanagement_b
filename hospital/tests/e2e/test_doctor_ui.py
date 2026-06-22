from hospital import models
from hospital.tests.e2e.base import WebUITestCase
from hospital.tests.helpers import DEFAULT_PASSWORD, create_doctor, create_patient


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
