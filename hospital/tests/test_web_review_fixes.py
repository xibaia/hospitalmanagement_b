from django.test import TestCase
from django.urls import reverse

from hospital.forms import MedicalRecordForm
from hospital.tests.helpers import (
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
