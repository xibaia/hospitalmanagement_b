from hospital.tests.e2e.base import WebUITestCase
from hospital.tests.helpers import (
    DEFAULT_PASSWORD,
    create_doctor,
    create_grouped_user,
    create_patient,
)


class AuthWebUITests(WebUITestCase):
    def test_admin_login_reaches_dashboard(self):
        admin = create_grouped_user("e2e_admin", "ADMIN")

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)

        self.assertIn("/admin-dashboard", self.page.url)

    def test_approved_doctor_login_reaches_dashboard(self):
        doctor_user, _ = create_doctor(username="e2e_approved_doctor", status=True)

        self.login("/doctorlogin", doctor_user.username, DEFAULT_PASSWORD)

        self.assertIn("/doctor-dashboard", self.page.url)

    def test_approved_patient_login_reaches_dashboard(self):
        patient_user, _ = create_patient(username="e2e_approved_patient", status=True)

        self.login("/patientlogin", patient_user.username, DEFAULT_PASSWORD)

        self.assertIn("/patient-dashboard", self.page.url)

    def test_pending_doctor_login_reaches_waiting_page(self):
        doctor_user, _ = create_doctor(username="e2e_pending_doctor", status=False)

        self.login("/doctorlogin", doctor_user.username, DEFAULT_PASSWORD)

        self.assert_page_contains("Your Account is not approved till now")

    def test_pending_patient_login_reaches_waiting_page(self):
        patient_user, _ = create_patient(username="e2e_pending_patient", status=False)

        self.login("/patientlogin", patient_user.username, DEFAULT_PASSWORD)

        self.assert_page_contains("Your Account is not approved till now")
