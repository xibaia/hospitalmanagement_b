from hospital import models
from hospital.tests.e2e.base import WebUITestCase
from hospital.tests.helpers import DEFAULT_PASSWORD, create_grouped_user


class AdminWebUITests(WebUITestCase):
    def test_admin_add_doctor_empty_form_stays_on_page(self):
        admin = create_grouped_user("e2e_add_doctor_admin", "ADMIN")

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-add-doctor")
        self.page.locator('button[type="submit"]').click()
        self.page.wait_for_load_state("networkidle")

        self.assertIn("/admin-add-doctor", self.page.url)
        self.assertEqual(models.Doctor.objects.count(), 0)

    def test_admin_add_patient_empty_form_stays_on_page(self):
        admin = create_grouped_user("e2e_add_patient_admin", "ADMIN")

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-add-patient")
        self.page.locator('button[type="submit"]').click()
        self.page.wait_for_load_state("networkidle")

        self.assertIn("/admin-add-patient", self.page.url)
        self.assertEqual(models.Patient.objects.count(), 0)
