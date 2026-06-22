from datetime import timedelta

from django.utils import timezone

from hospital import models
from hospital.tests.e2e.base import WebUITestCase
from hospital.tests.helpers import (
    DEFAULT_PASSWORD,
    create_activity,
    create_doctor,
    create_grouped_user,
    create_patient,
    create_record,
    create_station,
    create_volunteer,
)


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

    def test_admin_can_approve_pending_doctor_from_ui(self):
        admin = create_grouped_user("e2e_approve_doctor_admin", "ADMIN")
        _, doctor = create_doctor(
            username="e2e_pending_doctor_to_approve",
            status=False,
        )

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-approve-doctor")
        self.assert_page_contains(doctor.get_name)
        self.click_form_action(f"/approve-doctor/{doctor.id}")

        doctor.refresh_from_db()
        self.assertTrue(doctor.status)

    def test_admin_can_reject_pending_doctor_from_ui(self):
        admin = create_grouped_user("e2e_reject_doctor_admin", "ADMIN")
        doctor_user, doctor = create_doctor(
            username="e2e_pending_doctor_to_reject",
            status=False,
        )

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-approve-doctor")
        self.assert_page_contains(doctor.get_name)
        self.click_form_action(f"/reject-doctor/{doctor.id}")

        self.assertFalse(models.Doctor.objects.filter(id=doctor.id).exists())
        self.assertFalse(models.User.objects.filter(id=doctor_user.id).exists())

    def test_admin_can_approve_pending_patient_from_ui(self):
        admin = create_grouped_user("e2e_approve_patient_admin", "ADMIN")
        _, doctor = create_doctor(username="e2e_patient_approval_doctor")
        _, patient = create_patient(
            username="e2e_pending_patient_to_approve",
            assigned_doctor=doctor,
            status=False,
        )

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-approve-patient")
        self.assert_page_contains(patient.get_name)
        self.click_form_action(f"/approve-patient/{patient.id}")

        patient.refresh_from_db()
        self.assertTrue(patient.status)

    def test_admin_can_reject_pending_patient_from_ui(self):
        admin = create_grouped_user("e2e_reject_patient_admin", "ADMIN")
        _, doctor = create_doctor(username="e2e_patient_rejection_doctor")
        patient_user, patient = create_patient(
            username="e2e_pending_patient_to_reject",
            assigned_doctor=doctor,
            status=False,
        )

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-approve-patient")
        self.assert_page_contains(patient.get_name)
        self.click_form_action(f"/reject-patient/{patient.id}")

        self.assertFalse(models.Patient.objects.filter(id=patient.id).exists())
        self.assertFalse(models.User.objects.filter(id=patient_user.id).exists())

    def test_admin_can_create_approved_appointment_from_ui(self):
        admin = create_grouped_user("e2e_create_appointment_admin", "ADMIN")
        _, doctor = create_doctor(username="e2e_admin_appt_doctor")
        _, patient = create_patient(
            username="e2e_admin_appt_patient",
            assigned_doctor=doctor,
        )

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-add-appointment")
        self.page.locator('select[name="doctor"]').select_option(str(doctor.id))
        self.page.locator('select[name="patient"]').select_option(str(patient.id))
        self.page.locator('textarea[name="description"]').fill(
            "E2E admin-created appointment"
        )
        self.submit_first_form()

        self.assert_url_contains("/admin-view-appointment")
        appointment = models.Appointment.objects.get(
            description="E2E admin-created appointment"
        )
        self.assertTrue(appointment.status)
        self.assertEqual(appointment.doctor, doctor)
        self.assertEqual(appointment.patient, patient)

    def test_admin_can_approve_pending_appointment_from_ui(self):
        admin = create_grouped_user("e2e_approve_appointment_admin", "ADMIN")
        _, doctor = create_doctor(username="e2e_pending_appt_doctor")
        _, patient = create_patient(
            username="e2e_pending_appt_patient",
            assigned_doctor=doctor,
        )
        appointment = models.Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            patientName=patient.get_name,
            doctorName=doctor.get_name,
            description="E2E pending appointment approval",
            status=False,
        )

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-approve-appointment")
        self.assert_page_contains("E2E pending appointment approval")
        self.click_form_action(f"/approve-appointment/{appointment.id}")

        appointment.refresh_from_db()
        self.assertTrue(appointment.status)

    def test_admin_can_reject_pending_appointment_from_ui(self):
        admin = create_grouped_user("e2e_reject_appointment_admin", "ADMIN")
        _, doctor = create_doctor(username="e2e_reject_appt_doctor")
        _, patient = create_patient(
            username="e2e_reject_appt_patient",
            assigned_doctor=doctor,
        )
        appointment = models.Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            patientName=patient.get_name,
            doctorName=doctor.get_name,
            description="E2E pending appointment rejection",
            status=False,
        )

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-approve-appointment")
        self.assert_page_contains("E2E pending appointment rejection")
        self.click_form_action(f"/reject-appointment/{appointment.id}")

        self.assertFalse(models.Appointment.objects.filter(id=appointment.id).exists())

    def test_admin_can_view_medical_record_detail(self):
        admin = create_grouped_user("e2e_admin_record_admin", "ADMIN")
        _, doctor = create_doctor(username="e2e_admin_record_doctor")
        _, patient = create_patient(
            username="e2e_admin_record_patient",
            assigned_doctor=doctor,
        )
        record = create_record(
            patient=patient,
            doctor=doctor,
            chief_complaint="E2E admin record complaint",
            diagnosis="E2E admin record diagnosis",
        )

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-medical-records")
        self.assert_page_contains(record.visit_no)
        self.goto(f"/admin-view-record/{record.id}")

        self.assert_page_contains(patient.get_name)
        self.assert_page_contains(doctor.get_name)
        self.assert_page_contains("E2E admin record complaint")
        self.assert_page_contains("E2E admin record diagnosis")

    def test_admin_can_generate_patient_discharge_bill(self):
        admin = create_grouped_user("e2e_discharge_admin", "ADMIN")
        _, doctor = create_doctor(username="e2e_discharge_doctor")
        _, patient = create_patient(
            username="e2e_discharge_patient",
            assigned_doctor=doctor,
            symptoms="E2E discharge symptoms",
        )

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto(f"/discharge-patient/{patient.id}")
        self.page.locator('input[name="roomCharge"]').fill("200")
        self.page.locator('input[name="doctorFee"]').fill("100")
        self.page.locator('input[name="medicineCost"]').fill("120")
        self.page.locator('input[name="OtherCharge"]').fill("40")
        self.submit_first_form()

        self.assert_page_contains(patient.get_name)
        bill = models.PatientDischargeDetails.objects.get(patient=patient)
        expected_total = (
            bill.roomCharge
            + bill.doctorFee
            + bill.medicineCost
            + bill.OtherCharge
        )
        self.assertEqual(bill.total, expected_total)
        self.assertEqual(bill.assignedDoctorName, doctor.get_name)

    def test_admin_activity_pages_show_empty_leader_and_created_activity(self):
        admin = create_grouped_user("e2e_activity_admin", "ADMIN")
        create_activity(name="E2E existing activity", leader=None)
        start = timezone.now().replace(second=0, microsecond=0)
        end = start + timedelta(hours=2)

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-activity")
        self.assert_page_contains("E2E existing activity")
        self.assert_page_contains("未指定")

        self.goto("/admin-add-activity")
        self.page.locator('input[name="name"]').fill("E2E created activity")
        self.page.locator('input[name="location"]').fill("E2E activity location")
        self.page.locator('select[name="leader"]').select_option(str(admin.id))
        self.page.locator('input[name="start_time"]').fill(
            start.strftime("%Y-%m-%dT%H:%M")
        )
        self.page.locator('input[name="end_time"]').fill(
            end.strftime("%Y-%m-%dT%H:%M")
        )
        self.page.locator('textarea[name="description"]').fill(
            "E2E activity description"
        )
        self.page.locator('select[name="status"]').select_option("active")
        self.submit_first_form()

        self.assert_url_contains("/admin-activity")
        self.assertTrue(
            models.Activity.objects.filter(name="E2E created activity").exists()
        )

    def test_admin_station_pages_show_empty_supervisor_and_created_station(self):
        admin = create_grouped_user("e2e_station_admin", "ADMIN")
        create_station(name="E2E existing station", supervisor=None)

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-station")
        self.assert_page_contains("E2E existing station")
        self.assert_page_contains("—")

        self.goto("/admin-add-station")
        self.page.locator('input[name="name"]').fill("E2E created station")
        self.page.locator('input[name="address"]').fill("E2E station address")
        self.page.locator('input[name="latitude"]').fill("31.2304")
        self.page.locator('input[name="longitude"]').fill("121.4737")
        self.page.locator('input[name="phone"]').fill("02112345678")
        self.submit_first_form()

        self.assert_url_contains("/admin-station")
        self.assertTrue(
            models.Station.objects.filter(name="E2E created station").exists()
        )

    def test_admin_can_create_and_view_volunteer(self):
        admin = create_grouped_user("e2e_volunteer_admin", "ADMIN")
        _, existing = create_volunteer(username="e2e_existing_volunteer")

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-volunteer")
        self.assert_page_contains(existing.real_name)

        self.goto("/admin-add-volunteer")
        self.page.locator('input[name="first_name"]').fill("E2E")
        self.page.locator('input[name="last_name"]').fill("Volunteer")
        self.page.locator('input[name="username"]').fill("e2e_created_volunteer")
        self.page.locator('input[name="password"]').fill(DEFAULT_PASSWORD)
        self.page.locator('input[name="real_name"]').fill("E2E Created Vol")
        self.page.locator('input[name="mobile"]').fill("13700137001")
        self.submit_first_form()

        self.assert_url_contains("/admin-volunteer")
        self.assertTrue(
            models.Volunteer.objects.filter(
                real_name="E2E Created Vol"
            ).exists()
        )
