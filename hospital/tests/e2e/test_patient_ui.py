from hospital import models
from hospital.tests.e2e.base import WebUITestCase
from hospital.tests.helpers import DEFAULT_PASSWORD, create_patient


class PatientWebUITests(WebUITestCase):
    def test_patient_book_appointment_empty_form_stays_on_page(self):
        patient_user, _ = create_patient(username="e2e_empty_booking_patient")

        self.login("/patientlogin", patient_user.username, DEFAULT_PASSWORD)
        self.goto("/patient-book-appointment")
        self.page.locator('button[type="submit"]').click()
        self.page.wait_for_load_state("networkidle")

        self.assertIn("/patient-book-appointment", self.page.url)
        self.assertEqual(models.Appointment.objects.count(), 0)
