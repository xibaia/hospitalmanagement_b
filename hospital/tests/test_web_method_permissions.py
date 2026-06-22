from django.test import TestCase
from django.urls import reverse

from hospital import models
from hospital.tests.helpers import (
    DEFAULT_PASSWORD,
    create_activity,
    create_appointment,
    create_doctor,
    create_grouped_user,
    create_patient,
    create_station,
    create_volunteer,
)


class WebMethodPermissionTests(TestCase):
    def login(self, user):
        self.client.force_login(user)

    def test_admin_mutation_routes_reject_get_requests(self):
        admin = create_grouped_user("method_admin", "ADMIN")
        doctor_user, doctor = create_doctor(
            username="method_doctor",
            status=False,
        )
        patient_user, patient = create_patient(
            username="method_patient",
            status=False,
        )
        _, appt_doctor = create_doctor(username="method_appt_doctor")
        _, appt_patient = create_patient(
            username="method_appt_patient",
            assigned_doctor=appt_doctor,
        )
        appointment = create_appointment(
            patient=appt_patient,
            doctor=appt_doctor,
            description="Method appointment",
            status=False,
        )
        activity = create_activity(name="Method activity")
        station = create_station(name="Method station")
        _, volunteer = create_volunteer(
            username="method_volunteer",
            status=False,
        )
        real_name_max_length = volunteer._meta.get_field("real_name").max_length
        self.assertLessEqual(len(volunteer.real_name), real_name_max_length)
        self.login(admin)

        routes = [
            reverse("approve-doctor", args=[doctor.id]),
            reverse("reject-doctor", args=[doctor.id]),
            reverse("delete-doctor-from-hospital", args=[doctor.id]),
            reverse("approve-patient", args=[patient.id]),
            reverse("reject-patient", args=[patient.id]),
            reverse("delete-patient-from-hospital", args=[patient.id]),
            reverse("approve-appointment", args=[appointment.id]),
            reverse("reject-appointment", args=[appointment.id]),
            reverse("delete-activity", args=[activity.id]),
            reverse("delete-station", args=[station.id]),
            reverse("approve-volunteer", args=[volunteer.id]),
            reverse("reject-volunteer", args=[volunteer.id]),
        ]

        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertIn(response.status_code, {302, 405})

        self.assertTrue(models.Doctor.objects.filter(id=doctor.id).exists())
        self.assertTrue(models.User.objects.filter(id=doctor_user.id).exists())
        self.assertTrue(models.Patient.objects.filter(id=patient.id).exists())
        self.assertTrue(models.User.objects.filter(id=patient_user.id).exists())
        self.assertTrue(
            models.Appointment.objects.filter(id=appointment.id).exists()
        )
        self.assertTrue(models.Activity.objects.filter(id=activity.id).exists())
        self.assertTrue(models.Station.objects.filter(id=station.id).exists())
        self.assertTrue(
            models.Volunteer.objects.filter(id=volunteer.id).exists()
        )

    def test_doctor_cannot_post_delete_other_doctor_appointment(self):
        doctor_user, _ = create_doctor(username="method_owner_doctor")
        _, other_doctor = create_doctor(username="method_other_doctor")
        _, patient = create_patient(
            username="method_other_patient",
            assigned_doctor=other_doctor,
        )
        appointment = create_appointment(
            patient=patient,
            doctor=other_doctor,
            description="Protected appointment",
            status=True,
        )
        self.login(doctor_user)

        response = self.client.post(
            reverse("delete-appointment", args=[appointment.id])
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            models.Appointment.objects.filter(id=appointment.id).exists()
        )

    def test_role_pages_redirect_when_logged_in_as_wrong_role(self):
        doctor_user, _ = create_doctor(username="method_wrong_role_doctor")
        patient_user, _ = create_patient(username="method_wrong_role_patient")
        admin = create_grouped_user("method_wrong_role_admin", "ADMIN")

        cases = [
            (doctor_user, "/admin-dashboard"),
            (patient_user, "/doctor-dashboard"),
            (admin, "/patient-dashboard"),
        ]

        for user, path in cases:
            with self.subTest(user=user.username, path=path):
                self.client.logout()
                self.login(user)
                response = self.client.get(path)
                self.assertEqual(response.status_code, 302)
